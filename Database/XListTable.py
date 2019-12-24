#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2019/02/02
@file: DataTable.py
@function:
@modify:
"""
from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

from Utiltity.common import *
from Database.SqlRw import SqlAccess


class XListTable:
    def __init__(self, sql_db: SqlAccess):
        self.__sql_db = sql_db

    def add_to_list(self, name: str, reason: str):
        pass

    def remove_from_list(self, name: str):
        pass

    def get_name_list(self) -> [str]:
        pass



