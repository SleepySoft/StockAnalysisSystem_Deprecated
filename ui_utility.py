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


# -------------------------------------------------------------------------------------------------------

def horizon_layout(widgets: list) -> QHBoxLayout:
    layout = QHBoxLayout()
    for widget in widgets:
        layout.addWidget(widget)
    return layout


def create_v_group_box(title: str) -> (QGroupBox, QBoxLayout):
    group_box = QGroupBox(title)
    group_layout = QVBoxLayout()
    # group_layout.addStretch(1)
    group_box.setLayout(group_layout)
    return group_box, group_layout



