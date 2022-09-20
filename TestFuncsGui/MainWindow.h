#pragma once

#include <QMainWindow>

#include "ui_MainWindow.h"

#include "pch.h"
#include "ucPch.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget* parent = nullptr);
    ~MainWindow();

private:
    std::unique_ptr<Ui::MainWindow> ui;
};
