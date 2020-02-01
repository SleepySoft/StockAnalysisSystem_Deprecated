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
import copy
import traceback
import threading

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QHeaderView

from Utiltity.common import *
from Utiltity.ui_utility import *
from Utiltity.time_utility import *
from DataHub.DataHubEntry import *
from Database.UpdateTableEx import *
from stock_analysis_system import StockAnalysisSystem


DEFAULT_INFO = """数据更新界面说明：
1. 首先请配置好config.py里面的TS_TOKEN及NOSQL相关字段
2. 如果从零开始，请先更新Market.SecuritiesInfo以获取股票列表，后续功能方可正常运作
3. 由于采集本地数据范围需要从数据库中读取大量数据，故界面反应会较慢，后续会对此进行优化
4. 在首页更新财务信息会对所有股票执行一次，故耗时非常长，请做好挂机准备（Update Select未实现）
5. Force Update会拉取从1990年至今的数据，耗时非常长，请谨慎使用"""


class DataUpdateUi(QWidget):
    TABLE_HEADER_URI = ['', 'URI', 'Local Data Since', 'Local Data Until', 'Latest Update',
                        'Update Estimation', 'Sub Update', 'Update', 'Status']
    TABLE_HEADER_IDENTITY = ['', 'Identity', 'Local Data Since', 'Local Data Until', 'Latest Update',
                             'Update Estimation', 'Update', 'Status', '']
    # TODO: Auto detect
    HAS_DETAIL_LIST = ['Finance.Audit', 'Finance.BalanceSheet', 'Finance.IncomeStatement', 'Finance.CashFlowStatement']

    def __init__(self, data_hub_entry: DataHubEntry, update_table: UpdateTableEx):
        super(DataUpdateUi, self).__init__()
        self.__data_hub = data_hub_entry
        self.__data_center = self.__data_hub.get_data_center()
        self.__update_table = update_table

        # Page and level related
        self.__current_uri = ''
        self.__page = 0
        self.__item_per_page = 50

        # Thread and task related
        self.__lock = threading.Lock()
        self.__task_thread = None
        self.__update_pack = []     # [[uri, [identities] or None]]
        self.__update_force = False
        self.__progress_rate = ProgressRate()

        # Timer for update status
        self.__timer = QTimer()
        self.__timer.setInterval(1000)
        self.__timer.timeout.connect(self.on_timer)
        self.__timer.start()

        # UI related
        self.__info_panel = QLabel(DEFAULT_INFO)

        self.__table_main = EasyQTableWidget()
        self.__button_head_page = QPushButton('<<')
        self.__button_prev_page = QPushButton('<')
        self.__button_next_page = QPushButton('>')
        self.__button_tail_page = QPushButton('>>')
        self.__button_upper_level = QPushButton('↑')

        self.__button_refresh = QPushButton('Refresh')
        self.__button_batch_auto_update = QPushButton('Auto Update Select')
        self.__button_batch_force_update = QPushButton('Force Update Select')

        self.init_ui()

    # ---------------------------------------------------- UI Init -----------------------------------------------------

    def init_ui(self):
        self.__layout_control()
        self.__config_control()
        # self.update_uri_level()

    def __layout_control(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setMinimumSize(600, 400)
        main_layout.addWidget(self.__table_main)

        bottom_control_area = QHBoxLayout()
        main_layout.addLayout(bottom_control_area)

        bottom_right_area = QVBoxLayout()
        bottom_control_area.addWidget(self.__info_panel, 99)
        bottom_control_area.addLayout(bottom_right_area, 0)

        line = horizon_layout([self.__button_head_page, self.__button_prev_page,
                               self.__button_next_page, self.__button_tail_page,
                               self.__button_upper_level, self.__button_refresh])
        bottom_right_area.addLayout(line)

        line = horizon_layout([self.__button_batch_auto_update, self.__button_batch_force_update])
        bottom_right_area.addLayout(line)

    def __config_control(self):
        for _ in DataUpdateUi.TABLE_HEADER_URI:
            self.__table_main.insertColumn(0)
        self.__table_main.setHorizontalHeaderLabels(DataUpdateUi.TABLE_HEADER_URI)
        self.__table_main.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.__button_head_page.clicked.connect(partial(self.on_page_control, '<<'))
        self.__button_prev_page.clicked.connect(partial(self.on_page_control, '<'))
        self.__button_next_page.clicked.connect(partial(self.on_page_control, '>'))
        self.__button_tail_page.clicked.connect(partial(self.on_page_control, '>>'))
        self.__button_upper_level.clicked.connect(partial(self.on_page_control, '^'))
        self.__button_refresh.clicked.connect(partial(self.on_page_control, 'r'))

        # self.__button_batch_auto_update.connect(partial(self.on_page_control, 'r'))
        # self.__button_batch_force_update.connect(partial(self.on_page_control, 'r'))

    def on_detail_button(self, uri: str):
        print('Detail of ' + uri)
        self.__current_uri = uri
        self.__page = 0
        self.update_identity_level(uri, self.__page * self.__item_per_page, self.__item_per_page)

    def on_auto_update_button(self, uri: str, identity: str):
        print('Auto update ' + uri + ':' + str(identity))
        self.__update_pack = [[uri, identity]]
        self.__update_force = False
        self.execute_update_task()

    def on_force_update_button(self, uri: str, identity: str):
        print('Force update ' + uri + ':' + str(identity))
        self.__update_pack = [[uri, identity]]
        self.__update_force = True
        self.execute_update_task()

    def on_page_control(self, control: str):
        data_utility = self.__data_hub.get_data_utility()
        stock_list = data_utility.get_stock_list()
        max_page = len(stock_list) // self.__item_per_page

        if control == '<<':
            self.__page = 0
        elif control == '<':
            self.__page = max(self.__page - 1, 0)
        elif control == '>':
            self.__page = min(self.__page + 1, max_page)
        elif control == '>>':
            self.__page = max_page
        elif control == '^':
            self.__current_uri = ''
            self.update_uri_level()
        elif control == 'r':
            self.update_table()

        if control in ['<<', '<', '>', '>>', '^']:
            if self.__current_uri != '':
                self.update_table()

    def on_timer(self):
        for i in range(0, self.__table_main.rowCount()):
            if self.__current_uri == '':
                uri = self.__table_main.item(i, 1).text()
                if self.__progress_rate.has_progress(uri):
                    rate = self.__progress_rate.get_progress_rate(uri)
                    self.__table_main.item(i, 8).setText('%.2f%%' % (rate * 100))
                else:
                    self.__table_main.item(i, 8).setText(str(''))
            else:
                uri = self.__current_uri
                identity = self.__table_main.item(i, 1).text()
                if self.__progress_rate.has_progress([uri, identity]):
                    rate = self.__progress_rate.get_progress_rate([uri, identity])
                    self.__table_main.item(i, 7).setText('%.2f%%' % (rate * 100))
                else:
                    self.__table_main.item(i, 7).setText('')

    def closeEvent(self, event):
        if self.__task_thread is not None:
            QMessageBox.information(self,
                                    QtCore.QCoreApplication.translate('', '无法关闭窗口'),
                                    QtCore.QCoreApplication.translate('', '更新过程中无法关闭此窗口'),
                                    QMessageBox.Close, QMessageBox.Close)
            event.ignore()
        else:
            event.accept()

    # --------------------------------------------------------------------------------------

    def update_table(self):
        if self.__current_uri == '':
            self.update_uri_level()
        else:
            self.update_identity_level(self.__current_uri, self.__page * self.__item_per_page, self.__item_per_page)

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

    def work_around_for_update_pack(self):
        for i in range(0, len(self.__update_pack)):
            if self.__update_pack[i][0] == 'Market.TradeCalender':
                self.__update_pack[i][1] = ['SSE']
            elif self.__update_pack[i][0] in ['Finance.Audit', 'Finance.BalanceSheet',
                                              'Finance.IncomeStatement', 'Finance.CashFlowStatement']:
                if self.__update_pack[i][1] is None:
                    data_utility = self.__data_hub.get_data_utility()
                    stock_list = data_utility.get_stock_identities()
                    self.__update_pack[i][1] = stock_list

    # --------------------------------- Thread ---------------------------------

    def execute_update_task(self):
        self.work_around_for_update_pack()
        if self.__task_thread is None:
            self.__task_thread = threading.Thread(target=self.ui_task)
            self.__task_thread.start()
        else:
            print('Task already running...')
            QMessageBox.information(self,
                                    QtCore.QCoreApplication.translate('', '无法执行'),
                                    QtCore.QCoreApplication.translate('', '已经有更新在运行中，无法同时运行多个更新'),
                                    QMessageBox.Close, QMessageBox.Close)

    def ui_task(self):
        print('Update task start.')

        self.__lock.acquire()
        task = copy.deepcopy(self.__update_pack)
        force = self.__update_force
        self.__lock.release()

        self.__progress_rate.reset()
        for uri, identities in task:
            if identities is not None:
                self.__progress_rate.set_progress(uri, 0, len(identities))
                for identity in identities:
                    self.__progress_rate.set_progress([uri, identity], 0, 1)
            else:
                self.__progress_rate.set_progress(uri, 0, 1)

        for uri, identities in task:
            if identities is not None:
                for identity in identities:
                    self.__data_center.update_local_data(uri, identity, force=force)
                    self.__progress_rate.increase_progress([uri, identity])
                    self.__progress_rate.increase_progress(uri)
            else:
                self.__data_center.update_local_data(uri, force=force)
                self.__progress_rate.increase_progress(uri)
        self.__task_thread = None

        print('Update task finished.')


# ----------------------------------------------------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    data_hub = StockAnalysisSystem().get_data_hub_entry()
    update_table = StockAnalysisSystem().get_database_entry().get_update_table()
    dlg = WrapperQDialog(DataUpdateUi(data_hub, update_table))
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






































