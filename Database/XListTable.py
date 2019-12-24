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

import pandas as pd
from Utiltity.common import *
from Utiltity.time_utility import *
from Database.SqlRw import SqlAccess


class XListTable:
    FIELD = ['name', 'reason', 'comments', 'last_update']
    INDEX_NAME = 0
    INDEX_REASON = 1
    INDEX_COMMENTS = 2
    INDEX_LAST_UPDATE = 3

    def __init__(self, table: str, sql_db: SqlAccess):
        assert table != ''
        self.__table = table
        self.__sql_db = sql_db
        self.__local_data = pd.DataFrame(columns=XListTable.FIELD)

    def flush(self):
        self.__sql_db.DataFrameToDB(self.__table, self.__local_data)

    def reload(self):
        self.__sql_db.DataFrameFromDB(self.__table, XListTable.FIELD, '')

    def upsert_to_list(self, name: str, reason: str, comments: str = ''):
        self.remove_from_list(name)
        self.__local_data.loc[len(self.__local_data)] = [name, reason, comments, now()]

    def remove_from_list(self, name: str):
        name_field = XListTable.FIELD[XListTable.INDEX_NAME]
        self.__sql_db = self.__sql_db[self.__sql_db[name_field] != name]

    def get_name_list(self) -> [str]:
        name_field = XListTable.FIELD[XListTable.INDEX_NAME]
        return self.__local_data[name_field].tolist()

    def get_name_table(self) -> pd.DataFrame:
        return self.__local_data



