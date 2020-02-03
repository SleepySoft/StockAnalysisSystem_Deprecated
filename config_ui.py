#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/08/08
@file: DataTable.py
@function:
@modify:
"""
import traceback
import threading

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QLineEdit

from Utiltity.ui_utility import *
from stock_analysis_system import StockAnalysisSystem


class ConfigUi(QWidget):
    check_finish_signal = pyqtSignal()

    def __init__(self):
        super(ConfigUi, self).__init__()

        self.__line_ts_token = QLineEdit()
        self.__line_nosql_db_host = QLineEdit('localhost')
        self.__line_nosql_db_port = QLineEdit('27017')
        self.__line_nosql_db_user = QLineEdit()
        self.__line_nosql_db_pass = QLineEdit()
        self.__button_ok = QPushButton('OK')
        self.__label_information = QLabel()

        self.init_ui()

    # ---------------------------------------------------- UI Init -----------------------------------------------------

    def init_ui(self):
        self.__layout_control()
        self.__config_control()

    def __layout_control(self):
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        self.setMinimumSize(600, 400)

        main_layout.addWidget(QLabel('NoSql Host: '), 0, 0)
        main_layout.addWidget(self.__line_nosql_db_host, 0, 1)

        main_layout.addWidget(QLabel('NoSql Port: '), 0, 2)
        main_layout.addWidget(self.__line_nosql_db_port, 0, 3)

        main_layout.addWidget(QLabel('NoSql User: '), 1, 0)
        main_layout.addWidget(self.__line_nosql_db_user, 1, 1)

        main_layout.addWidget(QLabel('NoSql Pass: '), 1, 2)
        main_layout.addWidget(self.__line_nosql_db_pass, 1, 3)

        main_layout.addWidget(QLabel('Ts Token: '), 2, 0)
        main_layout.addWidget(self.__line_ts_token, 2, 1, 1, 3)

        main_layout.addWidget(QLabel('Status: '), 3, 0)
        main_layout.addWidget(self.__button_ok, 3, 3)

        main_layout.addWidget(self.__label_information, 4, 0, 1, 4)

    def __config_control(self):
        self.setWindowTitle('System Config')
        self.__button_ok.clicked.connect(self.on_button_ok)
        self.__label_information.setStyleSheet("QLabel{border:2px solid rgb(0, 0, 0);}")

        sas = StockAnalysisSystem()
        logs = sas.get_log_errors()

        self.__config_to_ui()
        self.__label_information.setText('\n'.join(logs))

    def on_button_ok(self):
        self.__ui_to_config()
        self.close()

    def __config_to_ui(self):
        sas = StockAnalysisSystem()
        config = sas.get_config()
        config.load_config()

        text = config.get('TS_TOKEN')
        self.__line_ts_token.setText(text)

        text = config.get('NOSQL_DB_HOST')
        self.__line_nosql_db_host.setText(text)
        self.__line_nosql_db_port.setText(config.get('NOSQL_DB_PORT'))
        self.__line_nosql_db_user.setText(config.get('NOSQL_DB_USER'))
        self.__line_nosql_db_pass.setText(config.get('NOSQL_DB_PASS'))

    def __ui_to_config(self):
        sas = StockAnalysisSystem()
        config = sas.get_config()

        config.set('TS_TOKEN', self.__line_ts_token.text())
        config.set('NOSQL_DB_HOST', self.__line_nosql_db_host.text())
        config.set('NOSQL_DB_PORT', self.__line_nosql_db_port.text())
        config.set('NOSQL_DB_USER', self.__line_nosql_db_user.text())
        config.set('NOSQL_DB_PASS', self.__line_nosql_db_pass.text())

        config.save_config()


# ----------------------------------------------------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    dlg = WrapperQDialog(ConfigUi())
    dlg.exec()


# ----------------------------------------------------------------------------------------------------------------------

def exception_hook(type, value, tback):
    # log the exception here
    print('Exception hook triggered.')
    print(type)
    print(value)
    print(tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)


sys.excepthook = exception_hook


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass






































