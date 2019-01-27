#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from functools import partial

import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QStyledItemDelegate, QTreeWidgetItem, QComboBox, QGroupBox, QBoxLayout
from collections import OrderedDict

import readme
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QHBoxLayout, QTableWidgetItem, \
    QWidget, QPushButton, QDockWidget, QLineEdit, QAction, qApp, QMessageBox, QDialog, QVBoxLayout, QLabel, QTextEdit, \
    QListWidget, QShortcut

from types import SimpleNamespace

from ui_module import *
from ui_utility import *


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

class MainWindow(QMainWindow):

    def __init__(self):

        # --------- Init Parent ---------
        QMainWindow.__init__(self)
        self.__translate = QtCore.QCoreApplication.translate

        # --------- Init Member ---------

        self.__menu_view = None

        # ---------- Deep Init ----------
        self.init_ui()
        self.init_menu()
        self.init_sub_window()

    # ----------------------------- Setup and UI -----------------------------

    def init_ui(self):
        widget = QWidget()
        main_layout = QHBoxLayout()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.setWindowTitle('Stock Analysis System - Sleepy')
        self.statusBar().showMessage('Ready')
        self.showFullScreen()

    def init_menu(self):
        menu_bar = self.menuBar()

        menu_view = menu_bar.addMenu('View')
        self.__menu_view = menu_view

    def init_sub_window(self):
        self.__add_sub_window(QWidget(), {
            'DockName': self.__translate('main', 'Example'),
            'DockArea': Qt.LeftDockWidgetArea,
            'DockShow': True,
            'DockFloat': True,
            'MenuName': self.__translate('main', 'Example'),
            'MenuPresent': True,
            'ActionName': self.__translate('main', 'Example'),
            'ActionShortcut': self.__translate('main', 'Ctrl+E'),
            'ActionPresent': True,
            'ActionTips': self.__translate('main', '串口Example模块'),
        })

    def __add_sub_window(self, window: QWidget, config: dict):
        sub_window_data = SimpleNamespace()
        sub_window_data.config = config
        self.__setup_sub_window_dock(window, config, sub_window_data)
        self.__setup_sub_window_menu(config, sub_window_data)
        self.__setup_sub_window_action(config, sub_window_data)

    def __setup_sub_window_dock(self, window: QWidget, config: dict, sub_window_data: SimpleNamespace):
        dock_name = config.get('DockName', '')
        dock_area = config.get('DockArea', Qt.NoDockWidgetArea)
        dock_show = config.get('DockShow', False)
        dock_float = config.get('DockFloat', False)

        dock_wnd = QDockWidget(dock_name, self)
        self.addDockWidget(dock_area, dock_wnd)

        dock_wnd.setWidget(window)
        if dock_float:
            dock_wnd.setFloating(True)
            dock_wnd.move(self.geometry().center() - dock_wnd.rect().center())
        if dock_show:
            dock_wnd.show()

        sub_window_data.dock_wnd = dock_wnd

    def __setup_sub_window_menu(self, config: dict, sub_window_data: SimpleNamespace):
        dock_name = config.get('DockName', '')
        menu_name = config.get('MenuName', dock_name)
        menu_present = config.get('MenuPresent', False)
        dock_wnd = sub_window_data.dock_wnd if hasattr(sub_window_data, 'dock_wnd') else None

        if menu_present and dock_wnd is not None:
            menu_view = self.__menu_view
            menu_entry = menu_view.addAction(menu_name)
            menu_entry.triggered.connect(partial(self.on_menu_selected, dock_wnd))
            sub_window_data.menu_entry = menu_entry
        else:
            sub_window_data.menu_entry = None

    def __setup_sub_window_action(self, config: dict, sub_window_data: SimpleNamespace):
        dock_name = config.get('DockName', '')
        action_name = config.get('ActionName', dock_name)
        action_shortcut = config.get('ActionShortcut', '')
        action_present = config.get('ActionPresent', False)
        action_tips = config.get('ActionTips', '')
        dock_wnd = sub_window_data.dock_wnd if hasattr(sub_window_data, 'dock_wnd') else None
        # menu_entry = sub_window_data.menu_entry if hasattr(sub_window_data, 'menu_entry') else None

        if action_present and dock_wnd is not None:
            action = QAction(action_name, self)
            if action_shortcut != '':
                action.setShortcut(action_shortcut)
            action.setStatusTip(action_tips)
            action.triggered.connect(partial(self.on_menu_selected, dock_wnd))
            # if menu_entry is not None:
            #     menu_entry.addAction(action)
        else:
            sub_window_data.menu_entry = None

    # ----------------------------- UI Events -----------------------------

    def on_menu_help(self):
        help_wnd = InfoDialog('Help', readme.TEXT)
        help_wnd.exec()

    def on_menu_about(self):
        QMessageBox.about(self, 'About', readme.ABOUT)

    def on_menu_selected(self, docker):
        if docker is not None:
            if docker.isVisible():
                docker.hide()
            else:
                docker.show()

    def closeEvent(self, event):
        """Generate 'question' dialog on clicking 'X' button in title bar.
        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        reply = QMessageBox.question(
            self, self.__translate('main', "退出"),
            self.__translate('main', "是否确认退出？"),
            QMessageBox.Close | QMessageBox.Cancel,
            QMessageBox.Cancel)

        if reply == QMessageBox.Close:
            sys.exit(0)
        else:
            pass




