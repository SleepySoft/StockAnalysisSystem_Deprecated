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

from PyQt5.QtWidgets import QLineEdit, QAbstractItemView, QFileDialog, QCheckBox, QHeaderView

from Utiltity.ui_utility import *
from Utiltity.time_utility import *
from DataHub.DataHubEntry import *
from stock_analysis_system import StockAnalysisSystem


class DataUpdateUi(QWidget):
    TABLE_HEADER_URI = ['', 'URI', 'Local Data Since', 'Local Data Until',
                        'Latest Update', 'Update Estimation', 'Sub Update', 'Update']
    TABLE_HEADER_IDENTITY = ['', 'Identity', 'Local Data Since', 'Local Data Until',
                             'Latest Update', 'Update Estimation', 'Update', 'Status']
    # TODO: Auto detect
    HAS_DETAIL_LIST = ['Finance.Audit', 'Finance.BalanceSheet', 'Finance.IncomeStatement', 'Finance.CashFlowStatement']

    def __init__(self):
        super(DataUpdateUi, self).__init__()
        self.__data_hub = StockAnalysisSystem().get_data_hub_entry()
        self.__data_center = self.__data_hub.get_data_center()
        self.__update_table = StockAnalysisSystem().get_database_entry().get_update_table()
        self.__table_main = EasyQTableWidget()

        self.__current_uri = ''
        self.__page = 0
        self.__item_per_page = 50

        self.init_ui()

    # ---------------------------------------------------- UI Init -----------------------------------------------------

    def init_ui(self):
        self.__layout_control()
        self.__config_control()
        self.update_uri_level()

    def __layout_control(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.setMinimumSize(600, 400)
        main_layout.addWidget(self.__table_main)

    def __config_control(self):
        for _ in DataUpdateUi.TABLE_HEADER_URI:
            self.__table_main.insertColumn(0)
        self.__table_main.setHorizontalHeaderLabels(DataUpdateUi.TABLE_HEADER_URI)
        self.__table_main.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def update_uri_level(self):
        self.__table_main.clear()
        self.__table_main.setRowCount(0)
        self.__table_main.setHorizontalHeaderLabels(DataUpdateUi.TABLE_HEADER_URI)

        for declare in DATA_FORMAT_DECLARE:
            line = []
            uri = declare[0]
            data_table, _ = self.__data_center.get_data_table(uri)

            # TODO: Fetching finance data's date range spends a lost of time because the data is huge.
            since, until = data_table.range(uri, None)
            update_since, update_until = self.__data_center.calc_update_range(uri)

            update_tags = uri.split('.')
            latest_update = self.__update_table.get_last_update_time(update_tags)

            line.append('')     # Place holder for check box
            line.append(uri)
            line.append(date2text(since) if since is not None else ' - ')
            line.append(date2text(until) if until is not None else ' - ')
            line.append(date2text(latest_update) if latest_update is not None else ' - ')

            if update_since is not None and update_until is not None:
                line.append(date2text(update_since) + ' - ' + date2text(update_until))
            else:
                line.append(' - ')
            line.append('-')    # Place holder for detail button
            line.append('')     # Place holder for update button
            line.append('')     # Place holder for status

            self.__table_main.AppendRow(line)
            index = self.__table_main.rowCount() - 1

            # Add check box
            check_item = QTableWidgetItem()
            check_item.setCheckState(QtCore.Qt.Unchecked)
            self.__table_main.setItem(index, 0, check_item)

            # Add detail button
            if uri in DataUpdateUi.HAS_DETAIL_LIST:
                button = QPushButton('Enter')
                button.clicked.connect(partial(self.on_detail_button, uri))
                self.__table_main.AddWidgetToCell(index, 6, button)

            # Add update button
            button_auto = QPushButton('Auto')
            button_force = QPushButton('Force')
            button_auto.clicked.connect(partial(self.on_auto_update_button, uri, None))
            button_force.clicked.connect(partial(self.on_force_update_button, uri, None))
            self.__table_main.AddWidgetToCell(index, 7, [button_auto, button_force])

    def update_identity_level(self, uri: str, offset: int, count: int):
        if uri == '':
            self.update_uri_level()
            return

        self.__table_main.clear()
        self.__table_main.setRowCount(0)
        self.__table_main.setHorizontalHeaderLabels(DataUpdateUi.TABLE_HEADER_IDENTITY)

        data_utility = self.__data_hub.get_data_utility()
        stock_list = data_utility.get_stock_list()

        for index in range(offset, offset + count):
            if index >= len(stock_list):
                break

            stock_identity, name = stock_list[index]
            data_table, _ = self.__data_center.get_data_table(uri)

            since, until = data_table.range(uri, stock_identity)
            update_since, update_until = self.__data_center.calc_update_range(uri, stock_identity)

            update_tags = uri.split('.')
            update_tags.append(stock_identity.replace('.', '_'))
            latest_update = self.__update_table.get_last_update_time(update_tags)

            line = []
            line.append('')     # Place holder for check box
            line.append(stock_identity)
            line.append(date2text(since) if since is not None else ' - ')
            line.append(date2text(until) if until is not None else ' - ')
            line.append(date2text(latest_update) if latest_update is not None else ' - ')

            if update_since is not None and update_until is not None:
                line.append(date2text(update_since) + ' - ' + date2text(update_until))
            else:
                line.append(' - ')
            line.append('')     # Place holder for update button
            line.append('')     # Place holder for status

            self.__table_main.AppendRow(line)
            index = self.__table_main.rowCount() - 1

            # Add check box
            check_item = QTableWidgetItem()
            check_item.setCheckState(QtCore.Qt.Unchecked)
            self.__table_main.setItem(index, 0, check_item)

            # Add update button
            button_auto = QPushButton('Auto')
            button_force = QPushButton('Force')
            button_auto.clicked.connect(partial(self.on_auto_update_button, uri, stock_identity))
            button_force.clicked.connect(partial(self.on_force_update_button, uri, stock_identity))
            self.__table_main.AddWidgetToCell(index, 6, [button_auto, button_force])

    def on_detail_button(self, uri: str):
        print('Detail of ' + uri)
        self.__current_uri = uri
        self.__page = 0
        self.update_identity_level(uri, self.__page * self.__item_per_page, self.__item_per_page)

    def on_auto_update_button(self, uri: str, identity: str):
        print('Auto update ' + uri + ':' + str(identity))
        self.__data_center.update_local_data(uri, identity)

    def on_force_update_button(self, uri: str, identity: str):
        print('Force update ' + uri + ':' + str(identity))
        self.__data_center.update_local_data(uri, identity, force=True)


# ----------------------------------------------------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    dlg = WrapperQDialog(DataUpdateUi())
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






































