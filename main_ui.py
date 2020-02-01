#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import Qt

from strategy_ui import *
from data_update_ui import *
from DataHub.DataHubUi import *
from Database.AliasTableUi import *
from stock_analysis_system import StockAnalysisSystem


# =========================================== InfoDialog ===========================================

class InfoDialog(QDialog):
    def __init__(self, title: str, text: str):
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

        # --------- init Parent ---------
        super(MainWindow, self).__init__()

        # --------- init Member ---------
        self.__translate = QtCore.QCoreApplication.translate

        # ---------- Modules and Sub Window ----------

        self.__data_hub_ui = DataUpdateUi()
        self.__data_update_ui = DataUpdateUi()
        self.__strategy_ui = StrategyUi()

        self.__alias_table_module = StockAnalysisSystem().get_database_entry().get_alias_table()
        self.__alias_table_module_ui = AliasTableUi(self.__alias_table_module)

        # ---------- Deep init ----------
        self.init_ui()
        self.init_menu()
        self.init_sub_window()

        self.modules_init()
        self.modules_ui_init()

    # ----------------------------- Setup and UI -----------------------------

    def init_ui(self):
        # widget = QWidget()
        # main_layout = QHBoxLayout()
        # widget.setLayout(main_layout)
        # self.setCentralWidget(widget)

        self.setWindowTitle('Stock Analysis System - Sleepy')

    def init_menu(self):
        pass

    def init_sub_window(self):
        self.add_sub_window(self.__data_update_ui, 'data_update_ui', {
            'DockName': self.__translate('main', '数据管理'),
            'DockArea': Qt.LeftDockWidgetArea,
            'DockShow': True,
            'DockFloat': False,
            'MenuPresent': True,
            'ActionTips': self.__translate('main', '数据管理'),
            'ActionShortcut': 'Ctrl+D',
        })

        self.add_sub_window(self.__strategy_ui, 'strategy_ui', {
            'DockName': self.__translate('main', '策略管理'),
            'DockArea': Qt.RightDockWidgetArea,
            'DockShow': True,
            'DockFloat': False,
            'MenuPresent': True,
            'ActionTips': self.__translate('main', '策略管理'),
            'ActionShortcut': 'Ctrl+S',
        })

        data_update_ui = self.get_sub_window('data_update_ui')
        strategy_ui = self.get_sub_window('strategy_ui')

        if data_update_ui is not None and strategy_ui is not None:
            self.splitDockWidget(data_update_ui.dock_wnd, strategy_ui.dock_wnd, Qt.Horizontal)

    def modules_init(self):
        self.__alias_table_module.init(True)

    def modules_ui_init(self):
        self.__alias_table_module_ui.Init()

    # ----------------------------- UI Events -----------------------------





