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

from Database.DatabaseRW import DatabaseRW


class Database:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.__sAsUtility = DatabaseRW('Data/sAsUtility.db')
        self.__sAsDailyData = DatabaseRW('Data/sAsDailyData.db')
        self.__sAsFinanceData = DatabaseRW('Data/sAsFinanceData.db')

    def GetUtilityDB(self) -> DatabaseRW:
        return self.__sAsUtility

    def GetDailyDataDB(self) -> DatabaseRW:
        return self.__sAsDailyData

    def FinanceDataDB(self) -> DatabaseRW:
        return self.__sAsFinanceData


