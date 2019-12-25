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
from PyQt5.QtWidgets import QLineEdit, QAbstractItemView, QFileDialog, QCheckBox

from Utiltity.ui_utility import *
from Database.XListTable import *


class XListTableUi(QWidget):
    def __init__(self, x_table: XListTable):
        super(XListTableUi, self).__init__()

        self.__x_table = x_table
        self.__main_table = QTableWidget(self)
        self.__translate = QtCore.QCoreApplication.translate

        self.__button_add_name = QPushButton(self.__translate('', '添加'))
        self.__button_del_name = QPushButton(self.__translate('', '删除'))
        self.__button_import_csv = QPushButton(self.__translate('', '导入'))

        self.init_ui()

    # ---------------------------------------------------- UI Init -----------------------------------------------------

    def init_ui(self):
        self.__layout_control()
        self.__config_control()

    def __layout_control(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(self.__main_table)

        sub_layout = QHBoxLayout()
        sub_layout.addWidget(self.__button_add_name)
        sub_layout.addWidget(self.__button_del_name)
        sub_layout.addWidget(self.__button_import_csv)
        main_layout.addLayout(sub_layout)

    def __config_control(self):
        self.__button_add_name.clicked.connect(self.on_button_add_name)
        self.__button_del_name.clicked.connect(self.on_button_del_name)
        self.__button_import_csv.clicked.connect(self.on_button_import_csv)

    # ---------------------------------------------------- UI Event ----------------------------------------------------

    def on_button_add_name(self):
        pass

    def on_button_del_name(self):
        pass

    def on_button_import_csv(self):
        pass

    # ---------------------------------------------------- pvivate -----------------------------------------------------

    def __refresh(self):
        df = self.__x_table.get_name_table()
        df_display = df.copy(False)
        df_display['']
        write_df_to_qtable(df_display, self.__main_table)


# ----------------------------------------------------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    dlg = WrapperQDialog(XListTableUi(), False)
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



