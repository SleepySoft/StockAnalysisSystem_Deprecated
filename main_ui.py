#!/usr/bin/python3
# -*- coding: utf-8 -*-
from functools import partial
from types import SimpleNamespace

from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QDialog, QPushButton, QMainWindow, QWidget, QDockWidget, QAction

from public.ui_utility import *
from AliasTable.AliasTable import *
from AliasTable.AliasTableUi import *


# =========================================== InfoDialog ===========================================

class InfoDialog(QDialog):
    def __init__(self, title, text):
        super().__init__()
        self.__text = text
        self.__title = title
        self.__button_ok = QPushButton('OK')
        self.__layout_main = QVBoxLayout()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.__title)

        self.__button_ok.clicked.connect(self.on_btn_click_ok)

        self.__layout_main.addWidget(QLabel(self.__text), 1)
        self.__layout_main.addWidget(self.__button_ok)
        self.setLayout(self.__layout_main)

    def on_btn_click_ok(self):
        self.close()


# =========================================== MainWindow ===========================================

class MainWindow(CommonMainWindow):

    def __init__(self):

        # --------- Init Parent ---------
        super(MainWindow, self).__init__()

        # --------- Init Member ---------
        self.__translate = QtCore.QCoreApplication.translate

        # ---------- Modules and Sub Window ----------

        self.__alias_table_module = AliasTable()
        self.__alias_table_module_ui = AliasTableUi(self.__alias_table_module)

        # ---------- Deep Init ----------
        self.init_ui()
        self.init_menu()
        self.init_sub_window()

        self.modules_init()
        self.modules_ui_init()

    # ----------------------------- Setup and UI -----------------------------

    def init_ui(self):
        widget = QWidget()
        main_layout = QHBoxLayout()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.setWindowTitle('Stock Analysis System - Sleepy')

    def init_menu(self):
        pass

    def init_sub_window(self):
        self.add_sub_window(self.__alias_table_module_ui, {
            'DockName': self.__translate('main', 'Alias Table'),
            'DockArea': Qt.LeftDockWidgetArea,
            'DockShow': True,
            'DockFloat': True,
            'MenuName': self.__translate('main', 'Alias Table'),
            'MenuPresent': True,
            'ActionName': self.__translate('main', 'Alias Table'),
            'ActionShortcut': self.__translate('main', 'Ctrl+A'),
            'ActionPresent': True,
            'ActionTips': self.__translate('main', 'Alias Table'),
        })

    def modules_init(self):
        self.__alias_table_module.Init(True)

    def modules_ui_init(self):
        self.__alias_table_module_ui.Init()

    # ----------------------------- UI Events -----------------------------





