#!/usr/bin/python3
# -*- coding: utf-8 -*-

import serial
import serial.tools.list_ports

from public.ui_utility import *


# -------------------------------------------------------------------------------------------------------

class AliasTableModule(QWidget):
    def __init__(self):
        super().__init__()
        self.__translate = QtCore.QCoreApplication.translate

        self.__table_alias = QTableWidget()
        self.__line_search = QLineEdit()
        self.__line_formal_name = QLineEdit()
        self.__list_aliases = QListWidget()
        self.__button_add = QPushButton(self.__translate('name_table', '添加'))
        self.__button_del = QPushButton(self.__translate('name_table', '删除'))
        self.__button_edit = QPushButton(self.__translate('name_table', '编辑'))

        self.__serial_timer = QTimer(self)
        self.__serial_timer.timeout.connect(self.on_serial_timer)

        self.init_ui()

    def init_ui(self):
        self.__layout_control()
        self.__config_control()

    def __layout_control(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        _translate = QtCore.QCoreApplication.translate

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        left_layout.addLayout(horizon_layout([QLabel(self.__translate('serial', '串口检测')), self.__button_serial_detect]))
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('serial', '串口选择')), self.__combo_serial_port]))
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('serial', '波特率：')), self.__combo_baud_rate]))
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('serial', '数据位：')), self.__combo_data_bit]))
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('serial', '校验位：')), self.__combo_check_bit]))
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('serial', '停止位：')), self.__combo_stop_bit]))
        left_layout.addLayout(horizon_layout([self.__button_open, self.__button_close]))
        left_layout.addWidget(self.__send_board)

        right_layout.addWidget(self.__io_board)

    def __config_control(self):
        self.__button_open.setEnabled(True)
        self.__button_close.setEnabled(False)

        self.__button_serial_detect.clicked.connect(self.on_btn_click_detect)
        self.__button_open.clicked.connect(self.on_btn_click_open)
        self.__button_close.clicked.connect(self.on_btn_click_close)

        self.__combo_baud_rate.addItem(self.__translate('serial', "115200"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "2400"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "4800"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "9600"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "14400"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "19200"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "38400"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "57600"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "76800"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "12800"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "230400"))
        self.__combo_baud_rate.addItem(self.__translate('serial', "460800"))

        self.__combo_data_bit.addItem(self.__translate('serial', "8"))
        self.__combo_data_bit.addItem(self.__translate('serial', "7"))
        self.__combo_data_bit.addItem(self.__translate('serial', "6"))
        self.__combo_data_bit.addItem(self.__translate('serial', "5"))

        self.__combo_check_bit.addItem(self.__translate('serial', "N"))

        self.__combo_stop_bit.addItem(self.__translate('serial', "1"))

    def on_btn_click_detect(self):
        port_list = list(serial.tools.list_ports.comports())
        self.__combo_serial_port.clear()
        for port in port_list:
            self.__combo_serial_port.addItem(port[0], '%s' % port[1])
        if len(port_list) == 0:
            self.__combo_serial_port.addItem(self.__translate('serial', "无串口"), '')

    def on_btn_click_open(self):
        self.__serial.port = self.__combo_serial_port.currentText()
        self.__serial.baudrate = int(self.__combo_baud_rate.currentText())
        self.__serial.bytesize = int(self.__combo_data_bit.currentText())
        self.__serial.stopbits = int(self.__combo_stop_bit.currentText())
        self.__serial.parity = self.__combo_check_bit.currentText()

        try:
            self.__serial.open()
        except Exception as e:
            QMessageBox.critical(self, self.__translate('serial', "串口错误"), self.__translate('serial', "此串口不能被打开！"))
            return
        finally:
            pass

        if self.__serial.isOpen():
            self.__serial_timer.start(10)
            self.__button_open.setEnabled(False)
            self.__button_close.setEnabled(True)
            # self.__group_serial_port.setTitle(self.__translate('serial', '串口配置（状态：已开启）'))

    def on_btn_click_close(self):
        self.__serial_timer.stop()
        try:
            self.__serial.close()
        except Exception as e:
            pass

        self.__button_open.setEnabled(True)
        self.__button_close.setEnabled(False)
        # self.__group_serial_port.setTitle(self.__translate('serial', '串口配置'))

    def on_serial_timer(self):
        self.receive_data()

    def on_send_data(self, data: bytes):
        self.send_data(data)

    def send_data(self, data: bytes):
        if self.__serial is not None and self.__serial.isOpen():
            sent = self.__serial.write(data)
            if sent > 0:
                self.__io_board.on_sent(data)

    def receive_data(self):
        try:
            received = self.__serial.inWaiting()
        except Exception as e:
            self.port_close()
            return
        finally:
            pass

        if received > 0:
            # self.__update_statistics(0, received)
            data = self.__serial.read(received)
            self.__io_board.on_received(data)
            # text = ' '.join(['{:02X}'.format(b) for b in data])
            # self.__text_sent.append(text)




