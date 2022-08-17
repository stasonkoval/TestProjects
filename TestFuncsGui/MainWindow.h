#pragma once

#include <QMainWindow>

#include "ui_MainWindow.h"

#include <pch.h>

#include "ucc/core/ucTypes.h"
#include "ucc/core/ucMisc.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget* parent = nullptr);
    ~MainWindow();

private:
    std::unique_ptr<Ui::MainWindow> ui;
};
