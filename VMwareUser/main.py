import asyncio
import getpass
import time
from pyVim.connect import SmartConnectNoSSL, SmartConnect  # подключение
from pyVmomi import vim  # список виртуальных
from termcolor import colored


class VMwareUser:
    def __version__(self):
        return "0.0.0.1"

    def __init__(self):
        self.connection = None  # подклчючение
        self.machines = {}  # список имён считанных машин
        self.apply_machines = []  # список имён машин,с которыми будут проводиться работы
        self.async_loop = asyncio.new_event_loop()  # цикл обработки асинхронных заданий

        self.available_apply_machines = {   # cловарь доступных списков машин для обработки
            "Clear Windows": [
                "Koval_Windows_10_1909",
                "Koval_Windows_10_20H2",
                "Koval_Windows_10_21H1"
            ],
            "Clear Linux": [
                "Koval_AltLinux_10.0",
                "Koval_AltLinux_8.2",
                "Koval_AltLinux_9.8",
                "Koval_AltLinuxK_10.0",
                "Koval_AltServer_10.0",
                "Koval_AltServer_9.2",
                "Koval_Astra_Orel_2.12",
                "Koval_Astra_Smolensk_1.7",
                "Koval_CentOS_7.9",
                "Koval_CentOS_8.4.2105",
                "Koval_Debian_11.1.0",
                "Koval_Fedora_35",
                "Koval_OpenSUSE_15.3",
                "Koval_RedOS_7.3.1",
                "Koval_Ubuntu_18.04",
                "Koval_Ubuntu_20.04"
            ]
        }

    def __del__(self):
        self.async_loop.close()

    def select_apply_machines(self):
        '''Задать список машин, с которыми будут вестить работы'''
        print("Выберите номер из списка:")
        while True:
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
                print(e)
                print("Введите корректный номер из списка:")
                continue

        for name, machine_names in self.available_apply_machines.items():
            if cmd == 0:
                self.apply_machines = machine_names
                break
            else:
                cmd -= 1
        print('Для обработки выбрано ', colored(str(len(self.apply_machines)), 'magenta'), ' виртуальных машин')

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
                print(colored("Не удалось подключиться или неверные авторизационные данные", 'red'))

    def load_all_vms(self):
        '''Загрузка списка виртуальных машин с сервера'''
        print("Загрузка списка виртуальных машин с сервера...")
        self.content = self.connection.content
        container = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.VirtualMachine], True)
        self.machines = {(managed_object_ref.name, managed_object_ref) for managed_object_ref in container.view}
        print('На VSphere обнаружено ', colored(str(len(self.machines)), 'magenta'), ' виртуальных машин')

    def get_machine_gen(self):
        '''Получить генератор машин для обработки'''
        return ((machine_name, machine_ref) for machine_name, machine_ref in self.machines
                if machine_name in self.apply_machines)

    def wait_for_tasks(self, tasks):
        '''Ожидание завершения задач'''
        print(colored('Ожидание завершения ', 'grey'), colored(str(len(tasks)), 'magenta'),
              colored(' задач...', 'grey'))

        async def wait_for_task(task):
            while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                time.sleep(.1)

        async_tasks = [self.async_loop.create_task(wait_for_task(task)) for task in tasks]
        self.async_loop.run_until_complete(asyncio.wait(async_tasks))
        print(colored('Выполнение ', 'grey'), colored(str(len(tasks)), 'magenta'),
              colored(' задач завершено', 'grey'))

    def revert_to_last_snapshot(self):
        '''Откатить к последнему снапшоту список выбранных машин'''
        machine_gen = self.get_machine_gen()
        tasks = []
        for name, vm in machine_gen:
            last_snapshot = sorted(vm.snapshot.rootSnapshotList, key=lambda snap: snap.createTime)[-1]
            tasks.append(last_snapshot.snapshot.RevertToSnapshot_Task())
            print("Откат машины", colored(name, 'green'), "к снапшоту", colored(last_snapshot.name, 'blue'))
        # Ожидание завершения всех заданий
        self.wait_for_tasks(tasks)

    def power_on_off(self, power_on: bool = True):
        '''Включение/выключение машин'''
        machine_gen = self.get_machine_gen()
        tasks = []
        for name, vm in machine_gen:
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

    while True:
        print(colored("==================================================", "grey"))
        cmd = input("""Введите номер команды:
0 - выход
1 - подключение
2 - выбрать список машин для обработки
4 - откатить машины к последнему снапшоту
7 - включить машины
8 - выключить машины
>> """
                    )
        try:
            cmd = int(cmd)
            if cmd not in (0, 1, 2, 4, 7, 8):
                raise Exception("Неверный номер команды")
        except Exception as e:
            print(e)
            continue

        if cmd == 0:
            break
        elif cmd == 1:
            wmware_user.connect()
        elif cmd == 2:
            wmware_user.select_apply_machines()
        elif cmd == 4:
            wmware_user.revert_to_last_snapshot()
        elif cmd == 7:
            wmware_user.power_on_off(True)
        elif cmd == 8:
            wmware_user.power_on_off(False)
