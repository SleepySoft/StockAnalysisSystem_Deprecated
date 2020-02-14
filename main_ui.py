#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import Qt
from PyQt5.QtWidgets import QMenu

from config_ui import *
from strategy_ui import *
from data_update_ui import *
from DataHub.DataHubUi import *
from Database.AliasTableUi import *
from Database.XListTableUi import *
from Utiltity.task_queue_ui import *
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
        super(MainWindow, self).__init__(hold_menu=True)

        # --------- init Member ---------

        self.__menu_config = None
        self.__translate = QtCore.QCoreApplication.translate

        # ---------- Modules and Sub Window ----------

        data_hub_entry = StockAnalysisSystem().get_data_hub_entry()
        strategy_entry = StockAnalysisSystem().get_strategy_entry()
        database_entry = StockAnalysisSystem().get_database_entry()
        update_table = database_entry.get_update_table()

        self.__data_hub_ui = DataHubUi(data_hub_entry.get_data_center())
        self.__strategy_ui = StrategyUi(data_hub_entry, strategy_entry)
        self.__data_update_ui = DataUpdateUi(data_hub_entry, update_table)

        self.__gray_list_ui = XListTableUi(database_entry.get_gray_table(), '灰名单')
        self.__black_list_ui = XListTableUi(database_entry.get_black_table(), '黑名单')
        self.__focus_list_ui = XListTableUi(database_entry.get_focus_table(), '关注名单')

        self.__alias_table_module = database_entry.get_alias_table()
        self.__alias_table_ui = AliasTableUi(self.__alias_table_module)
        self.__task_queue_ui = TaskQueueUi(StockAnalysisSystem().get_task_queue())

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
        config_action = QAction('系统配置（需要重新启动程序）', self)
        config_action.setStatusTip('系统配置')
        config_action.triggered.connect(self.on_action_config)

        self.__menu_config = QMenu('Config')
        self.__menu_config.addAction(config_action)

        menu_bar = self.menuBar()
        menu_bar.addMenu(self.menu_file)
        menu_bar.addMenu(self.menu_view)
        menu_bar.addMenu(self.__menu_config)
        menu_bar.addMenu(self.menu_help)

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

        self.add_sub_window(self.__data_hub_ui, 'data_hub_ui', {
            'DockName': self.__translate('main', '数据查阅'),
            'DockArea': Qt.RightDockWidgetArea,
            'DockShow': False,
            'DockFloat': False,
            'MenuPresent': True,
            'ActionTips': self.__translate('main', '数据查阅'),
            'ActionShortcut': 'Ctrl+B',
        })

        # -------------------------------------------------------------------------

        self.add_sub_window(self.__black_list_ui, 'black_list_ui', {
            'DockName': self.__translate('main', '黑名单'),
            'DockArea': Qt.NoDockWidgetArea,
            'DockShow': False,
            'DockFloat': True,
            'MenuPresent': True,
            'ActionTips': self.__translate('main', '黑名单'),
        })

        self.add_sub_window(self.__focus_list_ui, 'focus_list_ui', {
            'DockName': self.__translate('main', '关注名单'),
            'DockArea': Qt.NoDockWidgetArea,
            'DockShow': False,
            'DockFloat': True,
            'MenuPresent': True,
            'ActionTips': self.__translate('main', '关注名单'),
        })

        self.add_sub_window(self.__gray_list_ui, 'gray_list_ui', {
            'DockName': self.__translate('main', '灰名单'),
            'DockArea': Qt.NoDockWidgetArea,
            'DockShow': False,
            'DockFloat': True,
            'MenuPresent': True,
            'ActionTips': self.__translate('main', '灰名单'),
        })

        # -------------------------------------------------------------------------

        self.add_sub_window(self.__alias_table_ui, 'alias_table_ui', {
            'DockName': self.__translate('main', '别名表（考虑废弃）'),
            'DockArea': Qt.NoDockWidgetArea,
            'DockShow': False,
            'DockFloat': True,
            'MenuPresent': True,
            'ActionTips': self.__translate('main', '别名表'),
        })

        self.add_sub_window(self.__task_queue_ui, 'task_queue_ui', {
            'DockName': self.__translate('main', '任务管理'),
            'DockArea': Qt.NoDockWidgetArea,
            'DockShow': False,
            'DockFloat': True,
            'MenuPresent': True,
            'ActionTips': self.__translate('main', '任务管理'),
        })

        # -------------------------------------------------------------------------

        data_update_ui = self.get_sub_window('data_update_ui')
        strategy_ui = self.get_sub_window('strategy_ui')

        if data_update_ui is not None and strategy_ui is not None:
            self.splitDockWidget(data_update_ui.dock_wnd, strategy_ui.dock_wnd, Qt.Horizontal)

    def modules_init(self):
        self.__alias_table_module.init(True)

    def modules_ui_init(self):
        self.__alias_table_ui.Init()

    # ----------------------------- UI Events -----------------------------

    def on_action_config(self):
        dlg = WrapperQDialog(ConfigUi())
        dlg.exec()

    def closeEvent(self, event):
        if StockAnalysisSystem().can_sys_quit():
            StockAnalysisSystem().finalize()
            super().closeEvent(event)
        else:
            QMessageBox.information(self,
                                    QtCore.QCoreApplication.translate('main', '无法退出'),
                                    QtCore.QCoreApplication.translate('main', '有任务正在执行中，无法退出程序'),
                                    QMessageBox.Ok, QMessageBox.Ok)
            event.ignore()




