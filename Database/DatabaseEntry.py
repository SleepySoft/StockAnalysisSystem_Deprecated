# !usr/bin/env python
# -*- coding:utf-8 -*-

"""
@version:
author:Sleepy
@time: 2019/01/08
@file: DatabaseEntry.py
@function:
@modify:
"""

from os import sys, path
from pymongo import MongoClient
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import config
    import Database.UpdateTableEx as UpdateTableEx
    from Database.SqlRw import SqlAccess
    from Database.NoSqlRw import ItkvTable
except Exception as e:
    sys.path.append(root_path)

    import config
    import Database.UpdateTableEx as UpdateTableEx
    from Database.SqlRw import SqlAccess
    from Database.NoSqlRw import ItkvTable
finally:
    pass


class DatabaseEntry:
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
        data_path = root_path + '/Data/'

        self.__sAsUtility = SqlAccess(data_path + 'sAsUtility.db')
        self.__sAsDailyData = SqlAccess(data_path + 'sAsDailyData.db')
        self.__sAsFinanceData = SqlAccess(data_path + 'sAsFinanceData.db')
        self.__mongo_db_client = MongoClient(config.NOSQL_DB_HOST, config.NOSQL__DB_PORT, serverSelectionTimeoutMS=5)

        self.__update_table = UpdateTableEx.UpdateTableEx()
        self.__securities_table = ItkvTable(DatabaseEntry().get_mongo_db_client(),
                                            'StockAnalysisSystem', 'SecuritiesData')
        self.__finance_table = {
            'BalanceSheet': ItkvTable(DatabaseEntry().get_mongo_db_client(),
                                      'StockAnalysisSystem', 'BalanceSheet'),
            'IncomeStatement': ItkvTable(DatabaseEntry().get_mongo_db_client(),
                                         'StockAnalysisSystem', 'IncomeStatement'),
            'CashFlowStatement': ItkvTable(DatabaseEntry().get_mongo_db_client(),
                                           'StockAnalysisSystem', 'CashFlowStatement'),
        }

    # ------------------------------------------------- Database Entry -------------------------------------------------

    def get_utility_db(self) -> SqlAccess:
        return self.__sAsUtility

    def get_daily_data_db(self) -> SqlAccess:
        return self.__sAsDailyData

    def get_finance_data_db(self) -> SqlAccess:
        return self.__sAsFinanceData

    def get_mongo_db_client(self) -> MongoClient:
        return self.__mongo_db_client

    # -------------------------------------------------- Table Entry ---------------------------------------------------

    def get_update_table(self) -> UpdateTableEx:
        return self.__update_table

    def get_securities_table(self) -> ItkvTable:
        return self.__securities_table

    def get_finance_table(self, table_name: str) -> ItkvTable:
        return self.__finance_table.get(table_name)

