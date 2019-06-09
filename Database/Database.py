# !usr/bin/env python
# -*- coding:utf-8 -*-

"""
@version:
author:Sleepy
@time: 2019/01/08
@file: Database.py
@function:
@modify:
"""

import os
from SqlRw import SqlAccess

# from os import sys, path
# root_path = path.dirname(path.dirname(path.abspath(__file__)))
#
# try:
#     from Database.SqlRw import SqlAccess
# except Exception as e:
#     sys.path.append(root_path)
#
#     from SqlRw import SqlAccess
# finally:
#     pass


class Database:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
            cls._instance.__singleton_init()
        return cls._instance

    def __init__(self):
        # This function may be called multiple times.
        pass

    def __singleton_init(self):
        full_path = os.path.realpath(__file__)
        path, filename = os.path.split(full_path)
        data_path = path + '/../Data/'

        self.__sAsUtility = SqlAccess(data_path + 'sAsUtility.db')
        self.__sAsDailyData = SqlAccess(data_path + 'sAsDailyData.db')
        self.__sAsFinanceData = SqlAccess(data_path + 'sAsFinanceData.db')

        # self.__update_table = UpdateTable()

    def get_utility_db(self) -> SqlAccess:
        return self.__sAsUtility

    def get_daily_data_db(self) -> SqlAccess:
        return self.__sAsDailyData

    def finance_data_db(self) -> SqlAccess:
        return self.__sAsFinanceData

    # def get_update_table(self) -> UpdateTable:
    #     return self.__update_table

