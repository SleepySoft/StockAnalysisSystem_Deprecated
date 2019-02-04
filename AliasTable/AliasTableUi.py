#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/08/08
@file: AliasTable.py
@function:
@modify:
"""
from PyQt5.QtWidgets import QWidget, QTableWidget, QListWidget, QHBoxLayout, QLineEdit, QTableWidgetItem, \
    QAbstractItemView, QFileDialog

from public.ui_utility import *
from AliasTable.AliasTable import *


class AliasTableUi(QWidget):
    def __init__(self, alias_table: AliasTable):
        super().__init__()

        self.__alias_table = alias_table
        self.__translate = QtCore.QCoreApplication.translate

        self.__line_alias = QLineEdit()
        self.__line_standard = QLineEdit()
        self.__line_standard_edit = QLineEdit()
        self.__table_alias = EasyQTableWidget(0, 2)
        self.__table_standard_name = EasyQTableWidget(0, 2)

        self.__button_add = QPushButton(self.__translate('', '添加别名'))
        self.__button_del_alias = QPushButton(self.__translate('', '删除别名'))
        self.__button_load_csv = QPushButton(self.__translate('', '载入CSV'))

        self.__button_del_standard = QPushButton(self.__translate('', '删除标准名'))
        self.__button_update_standard = QPushButton(self.__translate('', '更新标准名'))

        self.init_ui()

    def init_ui(self):
        self.__layout_control()
        self.__config_control()

    def __layout_control(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.__table_alias)
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('', '别名：')), self.__line_alias]))
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('', '标准名：')), self.__line_standard]))
        left_layout.addLayout(horizon_layout([self.__button_add, self.__button_del_alias, self.__button_load_csv]))

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.__table_standard_name)
        right_layout.addLayout(horizon_layout([QLabel(self.__translate('', '标准名：')), self.__line_standard_edit,
                                               self.__button_del_standard, self.__button_update_standard]))

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)

    def __config_control(self):
        self.__table_alias.setHorizontalHeaderLabels(
            [self.__translate('', '别名'), self.__translate('', '标准名')])
        self.__table_alias.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__table_alias.setSelectionMode(QAbstractItemView.SingleSelection)

        self.__table_standard_name.setHorizontalHeaderLabels(
            [self.__translate('', '标准名'), self.__translate('', '别名数量')])
        self.__table_standard_name.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__table_standard_name.setSelectionMode(QAbstractItemView.SingleSelection)

        self.__table_alias.clicked.connect(self.on_click_table_alias)
        self.__table_standard_name.clicked.connect(self.on_click_table_standard_name)

        self.__button_add.clicked.connect(self.on_button_click_add)
        self.__button_del_alias.clicked.connect(self.on_button_click_del_alias)
        self.__button_load_csv.clicked.connect(self.on_button_click_load_csv)
        self.__button_del_standard.clicked.connect(self.on_button_click_del_standard)
        self.__button_update_standard.clicked.connect(self.on_button_click_update_standard)

    def on_click_table_alias(self):
        row_content = self.__table_alias.GetCurrentRow()
        if len(row_content) >= 2:
            self.__line_alias.setText(row_content[0])
            self.__line_standard.setText(row_content[1])

    def on_click_table_standard_name(self):
        standard_name = self.__table_standard_name.GetCurrentRow()
        if len(standard_name) >= 1:
            self.__line_standard_edit.setText(standard_name[0])

    def on_button_click_add(self):
        alias = self.__line_alias.text()
        standard = self.__line_standard.text()
        self.__alias_table.AddAlias(alias, standard)
        self.__alias_table.DumpToDB()
        self.__update_alias_table()
        self.__update_standard_table()

    def on_button_click_del_alias(self):
        select_model = self.__table_alias.selectionModel()
        if not select_model.hasSelection():
            return
        row_index = select_model.currentIndex().row()
        alias = self.__table_alias.model().index(row_index, 0).data()
        # standard = self.__table_alias.model().index(row_index, 1).data()
        self.__alias_table.DelAlias(alias)
        self.__alias_table.DumpToDB()
        self.__update_alias_table()
        self.__update_standard_table()

    def on_button_click_load_csv(self):
        file_path, ok = QFileDialog.getOpenFileName(self, 'Load CSV file', '', 'CSV Files (*.csv);;All Files (*)')
        if ok:
            self.__alias_table.LoadFromCsv(file_path, True)

    def on_button_click_del_standard(self):
        select_model = self.__table_standard_name.selectionModel()
        if not select_model.hasSelection():
            return
        row_index = select_model.currentIndex().row()
        standard = self.__table_standard_name.model().index(row_index, 0).data()
        self.__alias_table.DelStandardName(standard)
        self.__alias_table.DumpToDB()
        self.__update_alias_table()
        self.__update_standard_table()

    def on_button_click_update_standard(self):
        standard_new = self.__line_standard_edit.text()
        if standard_new == '':
            return
        select_model = self.__table_standard_name.selectionModel()
        if not select_model.hasSelection():
            return
        row_index = select_model.currentIndex().row()
        standard = self.__table_standard_name.model().index(row_index, 0).data()
        self.__alias_table.UpdateStandardName(standard, standard_new)
        self.__alias_table.DumpToDB()
        self.__update_alias_table()
        self.__update_standard_table()

    def __update_alias_table(self):
        aliases_standard_table = self.__alias_table.GetAliasStandardTable()
        self.__table_alias.setRowCount(0)
        for alias in sorted(aliases_standard_table.keys()):
            standard_name = aliases_standard_table[alias]
            row_count = self.__table_alias.rowCount()
            self.__table_alias.insertRow(row_count)
            self.__table_alias.setItem(row_count, 0, QTableWidgetItem(alias))
            self.__table_alias.setItem(row_count, 1, QTableWidgetItem(standard_name))

    def __update_standard_table(self):
        standard_name_list = self.__alias_table.GetStandardNameList()
        aliases_standard_table = self.__alias_table.GetAliasStandardTable()

        self.__table_standard_name.setRowCount(0)
        for standard_name in standard_name_list:
            alias_count = self.__count_alias(aliases_standard_table, standard_name)
            row_count = self.__table_standard_name.rowCount()
            self.__table_standard_name.insertRow(row_count)
            self.__table_standard_name.setItem(row_count, 0, QTableWidgetItem(standard_name))
            self.__table_standard_name.setItem(row_count, 1, QTableWidgetItem(str(alias_count)))

    def __count_alias(self, aliases_standard_table: dict, alias: str) -> int:
        count = 0
        for key in aliases_standard_table:
            if aliases_standard_table[key] == alias:
                count += 1
        return count

    # Interface

    def Init(self):
        self.__update_alias_table()
        self.__update_standard_table()



