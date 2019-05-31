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

from Database.SqlRw import SqlAccess


class Database:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.__sAsUtility = SqlAccess('Data/sAsUtility.db')
        self.__sAsDailyData = SqlAccess('Data/sAsDailyData.db')
        self.__sAsFinanceData = SqlAccess('Data/sAsFinanceData.db')

    def GetUtilityDB(self) -> SqlAccess:
        return self.__sAsUtility

    def GetDailyDataDB(self) -> SqlAccess:
        return self.__sAsDailyData

    def FinanceDataDB(self) -> SqlAccess:
        return self.__sAsFinanceData


