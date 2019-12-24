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
    import Utiltity.common as common
    from Database.SqlRw import SqlAccess
    from Database.NoSqlRw import ItkvTable
except Exception as e:
    sys.path.append(root_path)

    import config
    import Utiltity.common as common
    from Database.SqlRw import SqlAccess
    from Database.NoSqlRw import ItkvTable
finally:
    pass


class DatabaseEntry:
    def __init__(self, data_path: str = None):
        if data_path is None or not isinstance(data_path, str):
            data_path = root_path + '/Data/'

        self.__no_sql_tables = {}

        self.__sAsUtility = SqlAccess(data_path + 'sAsUtility.db')
        self.__mongo_db_client = MongoClient(config.NOSQL_DB_HOST, config.NOSQL__DB_PORT, serverSelectionTimeoutMS=5)

        import Database.AliasTable as AliasTable
        import Database.UpdateTableEx as UpdateTableEx

        self.__alias_table = AliasTable.AliasTable(self.__sAsUtility)
        self.__update_table = UpdateTableEx.UpdateTableEx(self.__sAsUtility)

    # ------------------------------------------------- Database Entry -------------------------------------------------

    def get_utility_db(self) -> SqlAccess:
        return self.__sAsUtility

    def get_mongo_db_client(self) -> MongoClient:
        return self.__mongo_db_client

    # ------------------------------------------------- SQL Table Entry ------------------------------------------------

    def get_alias_table(self):
        return self.__alias_table

    def get_update_table(self):
        return self.__update_table

    # ------------------------------------------------ NoSQL Table Entry -----------------------------------------------

    def query_nosql_table(self, db: str, table: str,
                          identity_field: str = 'Identity',
                          datetime_field: str = 'DateTime') -> ItkvTable:
        if db not in self.__no_sql_tables.keys():
            self.__no_sql_tables[db] = {}
        db_entry = self.__no_sql_tables.get(db)
        if table not in db_entry.keys():
            db_entry[table] = ItkvTable(self.get_mongo_db_client(), db, table, identity_field, datetime_field)
        return db_entry.get(table)

