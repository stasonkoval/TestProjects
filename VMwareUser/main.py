import asyncio
import getpass
import json
import os
import time
from pyVim.connect import SmartConnectNoSSL, SmartConnect  # подключение
from pyVmomi import vim  # список виртуальных
from termcolor import colored


class VMwareUser:
    def __version__(self):
        return "0.0.0.2"

    def __init__(self):
        self.connection = None  # подклчючение
        self.vsphere_machines = {}  # список имён считанных машин
        self.apply_machines = []  # список имён машин,с которыми будут проводиться работы
        self.async_loop = asyncio.new_event_loop()  # цикл обработки асинхронных заданий
        self.available_apply_machines = {}  # cловарь доступных списков машин для обработки

    def __del__(self):
        self.async_loop.close()

    def connect(self):
        '''Подключение к VSphere'''
        print("Подключение к VSphere")
        host = "192.168.13.138"
        for _ in range(3):
            try:
                user = input("Имя пользователя: ")
                pwd = getpass.getpass("Пароль: ")
                self.connection = SmartConnectNoSSL(host=host, user=user, pwd=pwd)
                self.load_all_vms()
                break
            except Exception as e:
                self.connection = None
                print(colored("Не удалось подключиться или неверные авторизационные данные", 'red'))
        # Выход из программы из-за ошибки подключения
        if not self.connection:
            raise Exception("Ошибка подключения")

    def load_all_vms(self):
        '''Загрузка списка виртуальных машин с сервера'''
        print("Загрузка списка виртуальных машин с сервера...")
        self.content = self.connection.content
        container = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.VirtualMachine], True)
        self.vsphere_machines = {(managed_object_ref.name, managed_object_ref) for managed_object_ref in container.view}
        print('На VSphere обнаружено ', colored(str(len(self.vsphere_machines)), 'magenta'), ' виртуальных машин')

    def load_available_apply_machines(self):
        "Загрузка словаря для обработки машин"
        print("Загрузка списков имён машин из файла...")
        try:
            file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "machine_names.json")
            file = open(file_path, "r", encoding="utf-8")
            file_data = file.read()
            file.close()
            self.available_apply_machines = json.loads(file_data)
        except Exception as e:
            print(colored(f"Во время загрузки списков машин из файла {file_path} произошла ошибка:\nksi {e}", "red"))
            # Выход из программы из-за ошибки загрузки словаря
            raise Exception("Ошибка загрузки списков машин")

    def select_apply_machines(self):
        '''Задать список машин, с которыми будут вестить работы'''
        print("Выберите номер списка машин, с которым планируется проводить работы:")
        for _ in range(5):
            count = 0
            for name, machine_names in self.available_apply_machines.items():
                print(str(count), ") ", name, " - ", str(len(machine_names)), ' машин')
                count += 1

            try:
                cmd = int(input(">>"))
                if cmd < 0 or cmd >= count:
                    raise Exception("Неверный номер команды")
                break
            except Exception as e:
                cmd = None
                print(e)
                print("Введите корректный номер списка:")
                continue
        if cmd == None:
            raise Exception("Список машин для обработки не выбран")

        for name, machine_names in self.available_apply_machines.items():
            if cmd == 0:
                # Проверка, что все машины в списке есть на VSphere
                vsphere_machine_names = [vsphere_machine[0] for vsphere_machine in self.vsphere_machines]
                machine_names_not_found = []
                for machine_name in machine_names:
                    if machine_name not in vsphere_machine_names:
                        machine_names_not_found.append(machine_name)
                if machine_names_not_found:
                    raise Exception(
                        f"В загруженном списке машин обнаружены имена, которых нет на сервере VSphere: \n {machine_names_not_found}")
                self.apply_machines = machine_names
                break
            else:
                cmd -= 1
        print('Для обработки выбрано ', colored(str(len(self.apply_machines)), 'magenta'), ' виртуальных машин')

    def machine_generator(self):
        '''Генератор машин для обработки'''
        return ((machine_name, machine_ref) for machine_name, machine_ref in self.vsphere_machines
                if machine_name in self.apply_machines)

    def shapshot_generator(self, vm_machine):
        '''Генератор рекурсивного обхода снапшотов'''
        def recursive_yield_child_snapshots(shapshots):
            for shapshot in shapshots:
                yield shapshot
                yield from recursive_yield_child_snapshots(shapshot.childSnapshotList)
        yield from recursive_yield_child_snapshots(vm_machine.snapshot.rootSnapshotList)

    def wait_for_tasks(self, tasks):
        '''Ожидание завершения задач'''
        print(colored('Ожидание завершения ', 'grey'), colored(str(len(tasks)), 'magenta'),
              colored(' задач...', 'grey'))
        if len(tasks) == 0:
            return None

        async def wait_for_task(task):
            while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                time.sleep(.1)

        async_tasks = [self.async_loop.create_task(wait_for_task(task)) for task in tasks]
        self.async_loop.run_until_complete(asyncio.wait(async_tasks))
        print(colored('Выполнение ', 'grey'), colored(str(len(tasks)), 'magenta'),
              colored(' задач завершено', 'grey'))

    def revert_to_snapshot_name(self):
        '''Откатить машины к снапшоту по указанному имени снапшота'''
        snapshot_name = str(input("Введите имя снапшота: "))
        tasks = []
        for name, vm in self.machine_generator():
            snapshot_not_found = True
            for snapshot in self.shapshot_generator(vm):
                if snapshot.name == snapshot_name:
                    tasks.append(snapshot.snapshot.RevertToSnapshot_Task())
                    print("Откат машины", colored(name, 'green'), "к снапшоту", colored(snapshot_name, 'blue'))
                    snapshot_not_found = False
                    break
            if snapshot_not_found:
                print("Для машины", colored(name, 'green'), "снапшот с именем", colored(snapshot_name, 'blue'),
                      colored("не найден", 'red'))
        # Ожидание завершения всех заданий
        self.wait_for_tasks(tasks)

    def revert_to_last_snapshot(self):
        '''Откатить машины к последнему снапшоту'''
        tasks = []
        for name, vm in self.machine_generator():
            last_snapshot = sorted(vm.snapshot.rootSnapshotList, key=lambda snap: snap.createTime)[-1]
            tasks.append(last_snapshot.snapshot.RevertToSnapshot_Task())
            print("Откат машины", colored(name, 'green'), "к снапшоту", colored(last_snapshot.name, 'blue'))
        # Ожидание завершения всех заданий
        self.wait_for_tasks(tasks)

    def power_on_off(self, power_on: bool = True):
        '''Включение/выключение машин'''
        tasks = []
        for name, vm in self.machine_generator():
            if power_on:
                tasks.append(vm.PowerOnVM_Task())
                print("Включение машины", colored(name, 'green'))
            else:
                tasks.append(vm.PowerOffVM_Task())
                print("Выключение машины", colored(name, 'green'))
        # Ожидание завершения всех заданий
        self.wait_for_tasks(tasks)


if __name__ == '__main__':
    wmware_user = VMwareUser()
    print("Версия", wmware_user.__version__())

    try:
        wmware_user.connect()
        print(colored("==================================================", "grey"))
        wmware_user.load_available_apply_machines()
        wmware_user.select_apply_machines()


    except Exception as e:
        print(colored(str(e), "red"))
        exit()

    while True:
        print(colored("==================================================", "grey"))
        cmd = input("""Введите номер команды:
0 - выход
1 - откатить машины к снапшоту по указанному имени снапшота
2 - откатить машины к последнему снапшоту
4 - включить машины
5 - выключить машины
>> """
                    )
        try:
            cmd = int(cmd)
            if cmd == 0:
                break
            elif cmd == 1:
                wmware_user.revert_to_snapshot_name()
            elif cmd == 2:
                wmware_user.revert_to_last_snapshot()
            elif cmd == 4:
                wmware_user.power_on_off(True)
            elif cmd == 5:
                wmware_user.power_on_off(False)
            else:
                raise Exception("Неверный номер команды")

        except Exception as e:
            print(e)
            continue
