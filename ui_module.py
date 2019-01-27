#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
from functools import partial

import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QStyledItemDelegate, QTreeWidgetItem, QComboBox, QGroupBox, QBoxLayout
from collections import OrderedDict

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QHBoxLayout, QTableWidgetItem, \
    QWidget, QPushButton, QDockWidget, QLineEdit, QAction, qApp, QMessageBox, QDialog, QVBoxLayout, QLabel, QTextEdit, \
    QListWidget, QShortcut, QCheckBox

from ui_utility import *


# -------------------------------------------------------------------------------------------------------
#
class SendBoard(QWidget):
    """handler should implement on_send_data(data: bytes)"""
    def __init__(self, handler):
        super().__init__()
        self.__handler = handler
        self.__translate = QtCore.QCoreApplication.translate

        self.__text_send = QTextEdit()
        self.__check_hex = QCheckBox(self.__translate('serial', 'HEX'))
        self.__button_send = QPushButton(self.__translate('serial', '发送'))

        self.init_ui()

    def init_ui(self):
        self.__layout_control()
        self.__config_control()

    def __layout_control(self):
        main_layout = QVBoxLayout()
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        _translate = QtCore.QCoreApplication.translate

        main_layout.addWidget(self.__text_send)
        main_layout.addLayout(horizon_layout([self.__check_hex, self.__button_send]))

    def __config_control(self):
        self.__button_send.clicked.connect(self.on_btn_send)

    def on_btn_send(self) -> bytes:
        hex = self.__check_hex.isChecked()
        text = self.__text_send.toPlainText()

        try:
            if hex:
                data_arr = bytearray()
                hex_chars = text.split(' ')
                for hex_char in hex_chars:
                    data_arr.append(int(hex_char.strip(), 16))
                data = bytes(data_arr)
            else:
                data = text.encode('utf-8')
        except Exception as e:
            data = None
            print(str(e))
            QMessageBox.critical(self, self.__translate('serial', "输入错误"), self.__translate('serial', "非法输入"))
        finally:
            pass

        if data is not None and self.__handler is not None:
            self.__handler.on_send_data(data)


class IoBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.__translate = QtCore.QCoreApplication.translate

        self.__sent_count = 0
        self.__recv_count = 0
        self.__sent_bytes = bytearray()
        self.__recv_bytes = bytearray()
        self.__line_recv_len = QLineEdit('0')
        self.__line_sent_len = QLineEdit('0')

        self.__text_sent = QTextEdit()
        self.__text_recv = QTextEdit()
        self.__check_sent_hex = QCheckBox('HEX')
        self.__check_recv_hex = QCheckBox('HEX')
        self.__button_clr_sent = QPushButton(self.__translate('serial', '清空发送'))
        self.__button_clr_recv = QPushButton(self.__translate('serial', '清空接收'))

        self.init_ui()

    def init_ui(self):
        self.__layout_control()
        self.__config_control()

    def __layout_control(self):
        main_layout = QVBoxLayout()
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        _translate = QtCore.QCoreApplication.translate

        main_layout.addLayout(horizon_layout(
            [QLabel(self.__translate('serial', '已发送：')), self.__line_sent_len, self.__check_sent_hex, self.__button_clr_sent]))
        main_layout.addWidget(self.__text_sent)

        main_layout.addLayout(horizon_layout(
            [QLabel(self.__translate('serial', '已接收：')), self.__line_recv_len, self.__check_recv_hex, self.__button_clr_recv]))
        main_layout.addWidget(self.__text_recv)

    def __config_control(self):
        self.__check_sent_hex.setChecked(True)
        self.__check_recv_hex.setChecked(True)
        self.__check_sent_hex.clicked.connect(self.on_check_click_sent_hex)
        self.__check_recv_hex.clicked.connect(self.on_check_click_recv_hex)

        self.__button_clr_sent.clicked.connect(self.on_btn_click_clr_sent)
        self.__button_clr_recv.clicked.connect(self.on_btn_click_clr_recv)

    def on_btn_click_clr_sent(self):
        self.__line_sent_len.setText('0')
        self.__text_sent.setText('')
        self.__sent_bytes.clear()
        self.__sent_count = 0

    def on_btn_click_clr_recv(self):
        self.__line_recv_len.setText('0')
        self.__text_recv.setText('')
        self.__recv_bytes.clear()
        self.__recv_count = 0

    def on_check_click_sent_hex(self):
        hex = self.__check_sent_hex.isChecked()
        self.__text_sent.clear()
        if hex:
            self.__text_sent.setText(' '.join(['{:02X}'.format(b) for b in self.__sent_bytes]))
        else:
            self.__text_sent.setText(self.__sent_bytes.decode('utf-8'))

    def on_check_click_recv_hex(self):
        hex = self.__check_recv_hex.isChecked()
        self.__text_recv.clear()
        if hex:
            self.__text_recv.setText(' '.join(['{:02X}'.format(b) for b in self.__recv_bytes]))
        else:
            self.__text_recv.setText(self.__recv_bytes.decode('utf-8'))

    # ----------------------------------------- Interface -----------------------------------------

    def on_received(self, data: bytes):
        hex = self.__check_recv_hex.isChecked()
        recv_len = len(data)
        if recv_len > 0:
            self.__recv_bytes.extend(data)
            self.__update_statistics(0, recv_len)
            if hex:
                text = ' '.join(['{:02X}'.format(b) for b in data])
                self.__text_recv.append(text)
            else:
                self.__text_recv.append(data.decode('utf-8'))

    def on_sent(self, data: bytes):
        hex = self.__check_sent_hex.isChecked()
        sent_len = len(data)
        if sent_len > 0:
            self.__sent_bytes.extend(data)
            self.__update_statistics(sent_len, 0)
            if hex:
                text = ' '.join(['{:02X}'.format(b) for b in data])
                self.__text_sent.append(text)
            else:
                self.__text_sent.append(data.decode('utf-8'))

    # ------------------------------------------ Private ------------------------------------------

    def __update_statistics(self, sent: int, recv: int):
        self.__sent_count = self.__sent_count + sent
        self.__recv_count = self.__recv_count + recv
        self.__line_sent_len.setText(str(self.__sent_count))
        self.__line_recv_len.setText(str(self.__recv_count))


# -------------------------------------------------------------------------------------------------------

class SerialModule(QWidget):
    def __init__(self):
        super().__init__()
        self.__translate = QtCore.QCoreApplication.translate

        self.__io_board = IoBoard()
        self.__send_board = SendBoard(self)
        self.__serial = serial.Serial()

        self.__combo_serial_port = QComboBox()
        self.__combo_baud_rate   = QComboBox()
        self.__combo_data_bit    = QComboBox()
        self.__combo_check_bit   = QComboBox()
        self.__combo_stop_bit    = QComboBox()

        self.__button_open = QPushButton(self.__translate('serial', '打开串口'))
        self.__button_close = QPushButton(self.__translate('serial', '关闭串口'))
        self.__button_serial_detect = QPushButton(self.__translate('serial', '检测'))

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

        # if self.s__serial.isOpen():
        #     input_s = self.s3__send_text.toPlainText()
        #     if input_s != "":
        #         # 非空字符串
        #         if self.hex_send.isChecked():
        #             # hex发送
        #             input_s = input_s.strip()
        #             send_list = []
        #             while input_s != '':
        #                 try:
        #                     num = int(input_s[0:2], 16)
        #                 except ValueError:
        #                     QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
        #                     return None
        #                 input_s = input_s[2:].strip()
        #                 send_list.append(num)
        #             input_s = bytes(send_list)
        #         else:
        #             # ascii发送
        #             input_s = (input_s + '\r\n').encode('utf-8')
        #
        #         num = self.s__serial.write(input_s)
        #         self.data_num_sended += num
        #         self.lineEdit_2.setText(str(self.data_num_sended))
        # else:
        #     pass

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

        #     num = len(data)
        #     # hex显示
        #     if self.hex_receive.checkState():
        #         out_s = ''
        #         for i in range(0, len(data)):
        #             out_s = out_s + '{:02X}'.format(data[i]) + ' '
        #         self.s2__receive_text.insertPlainText(out_s)
        #     else:
        #         # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
        #         self.s2__receive_text.insertPlainText(data.decode('iso-8859-1'))
        #
        #     # 统计接收字符的数量
        #     self.data_num_received += num
        #     self.lineEdit.setText(str(self.data_num_received))
        #
        #     # 获取到text光标
        #     textCursor = self.s2__receive_text.textCursor()
        #     # 滚动到底部
        #     textCursor.movePosition(textCursor.End)
        #     # 设置光标到text中去
        #     self.s2__receive_text.setTextCursor(textCursor)
        # else:
        #     pass

    # def __update_statistics(self, sent: int, recv: int):
    #     self.__sent_count = self.__sent_count + sent
    #     self.__recv_count = self.__recv_count + recv
    #     self.__line_sent_len.setText(str(self.__sent_count))
    #     self.__line_recv_len.setText(str(self.__recv_count))


# -------------------------------------------------------------------------------------------------------

class MQTTModule(QWidget):
    def __init__(self):
        super().__init__()
        self.__translate = QtCore.QCoreApplication.translate

        from MQTTClient import MQTTClient
        self.__mqtt_client = MQTTClient()
        self.__io_board = IoBoard()
        self.__connected = False

        self.__line_host = QLineEdit()
        self.__line_port = QLineEdit()
        self.__line_user = QLineEdit()
        self.__line_passwd = QLineEdit()

        self.__button_connect = QPushButton(self.__translate('mqtt', '连接'))
        self.__button_disconnect = QPushButton(self.__translate('mqtt', '断开'))

        # MQTT input/subscribe

        self.__line_subscribe = QLineEdit()
        self.__list_subscribe = QListWidget()
        self.__button_subscribe = QPushButton(self.__translate('mqtt', '订阅'))
        self.__button_unsubscribe = QPushButton(self.__translate('mqtt', '删除订阅'))

        # MQTT publish

        self.__line_topic = QLineEdit()
        self.__send_board = SendBoard(self)

        self.__mqtt_timer = QTimer(self)
        self.__mqtt_timer.timeout.connect(self.on_mqtt_timer)

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

        left_layout.addLayout(horizon_layout([QLabel(self.__translate('mqtt', '服务器：')), self.__line_host]))
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('mqtt', '端口  ：')), self.__line_port]))
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('mqtt', '用户名：')), self.__line_user]))
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('mqtt', '密码  ：')), self.__line_passwd]))
        left_layout.addLayout(horizon_layout([self.__button_connect, self.__button_disconnect]))

        left_layout.addWidget(self.__list_subscribe)
        left_layout.addLayout(horizon_layout([QLabel(self.__translate('serial', '订阅主题')), self.__line_subscribe]))
        left_layout.addLayout(horizon_layout([self.__button_subscribe, self.__button_unsubscribe]))
        left_layout.addWidget(self.__send_board)

        right_layout.addWidget(self.__io_board)

        # right_layout.addLayout(horizon_layout([QLabel(self.__translate('serial', '发送记录：')), self.__button_clr_sent]))
        # right_layout.addWidget(self.__text_sent)
        #
        # right_layout.addLayout(horizon_layout([QLabel(self.__translate('serial', '接收记录：')), self.__button_clr_recv]))
        # right_layout.addWidget(self.__text_recv)

    def __config_control(self):
        self.__button_connect.setEnabled(True)
        self.__button_disconnect.setEnabled(False)

        self.__button_connect.clicked.connect(self.on_btn_click_connect)
        self.__button_disconnect.clicked.connect(self.on_btn_click_disconnect)
        self.__button_subscribe.clicked.connect(self.on_btn_click_subscribe)
        self.__button_unsubscribe.clicked.connect(self.on_btn_click_unsubscribe)

    def on_btn_click_connect(self):
        try:
            host = str(self.__line_host.text())
            port = int(self.__line_port.text())
            user = str(self.__line_user.text())
            passwd = str(self.__line_passwd.text())
            passwd = None if passwd == '' else passwd

            self.__mqtt_client.config_host(host, port)
            self.__mqtt_client.config_auth(user, passwd)
            self.__connected = self.__mqtt_client.start()

            if self.__connected:
                self.__mqtt_timer.start(100)
                self.__button_connect.setEnabled(False)
                self.__button_disconnect.setEnabled(True)
        except Exception as e:
            print(str(e))
            QMessageBox.critical(self, self.__translate('mqtt', "连接错误"), self.__translate('mqtt', "链接失败！"))
        finally:
            pass

    def on_btn_click_disconnect(self):
        if self.__mqtt_client is not None:
            self.__mqtt_client.disconnect()
            self.__mqtt_timer.stop()

    def on_btn_click_subscribe(self):
        topic = self.__line_subscribe.text()
        if self.__mqtt_client is not None:
            try:
                self.__mqtt_client.subscribe(topic)
                self.__list_subscribe.addItem(topic)
            except Exception as e:
                print(str(e))
                QMessageBox.critical(self, self.__translate('mqtt', "订阅失败"), self.__translate('mqtt', "订阅失败！"))
            finally:
                pass

    def on_btn_click_unsubscribe(self):
        items = self.__list_subscribe.selectedItems()
        if items is not None and len(items) > 0 and self.__mqtt_client is not None:
            for item in items:
                self.__mqtt_client.unsubscribe(item.text())
                self.__list_subscribe.takeItem(self.__list_subscribe.row(item))

    def on_mqtt_timer(self):
        if self.__mqtt_client is not None:
            if self.__mqtt_client.is_running:
                messages = self.__mqtt_client.read()
                for msg in messages:
                    self.__io_board.on_received(msg[1].payload)
            else:
                self.__connected = False
                self.__mqtt_timer.stop()
                self.__button_connect.setEnabled(True)
                self.__button_disconnect.setEnabled(False)
















