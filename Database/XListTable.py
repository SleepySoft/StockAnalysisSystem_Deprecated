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

    def clear(self):
        self.__local_data = pd.DataFrame(columns=XListTable.FIELD)

    def flush(self):
        self.__sql_db.DataFrameToDB(self.__table, self.__local_data)

    def reload(self):
        self.__local_data = self.__sql_db.DataFrameFromDB(self.__table, XListTable.FIELD, '')

    def upsert_to_list(self, name: str, reason: str, comments: str = ''):
        self.remove_from_list(name)
        self.__local_data.loc[len(self.__local_data)] = [name, reason, comments, now()]

    def remove_from_list(self, name: str):
        name_field = XListTable.FIELD[XListTable.INDEX_NAME]
        self.__local_data = self.__local_data[self.__local_data[name_field] != name]

    def get_name_list(self) -> [str]:
        name_field = XListTable.FIELD[XListTable.INDEX_NAME]
        return self.__local_data[name_field].tolist()

    def get_name_table(self) -> pd.DataFrame:
        return self.__local_data


# ----------------------------------------------------------------------------------------------------------------------

def __prepare_x_table(name: str) -> XListTable:
    data_path = root_path + '/Temporary/'
    sql_db = SqlAccess(data_path + 'sAsUtility.db')
    x_table = XListTable(name, sql_db)
    return x_table


def test_basic():
    x_table = __prepare_x_table('GrayTable')
    x_table.clear()
    x_table.flush()

    x_table.upsert_to_list('100000.SSZ', 'reason1', 'comments1')
    x_table.upsert_to_list('100000.SSZ', 'reason2', 'comments2')
    x_table.upsert_to_list('100000.SSZ', 'reason3', 'comments3')

    df = x_table.get_name_table()
    assert len(df) == 1

    line = df.iloc[0].values.tolist()
    assert line[0] == '100000.SSZ'
    assert line[1] == 'reason3'
    assert line[2] == 'comments3'
    print('Last update: ' + str(line[3]))

    x_table.upsert_to_list('100001.SSZ', 'reason5', 'comments5')
    x_table.upsert_to_list('100002.SSZ', 'reason6', 'comments6')
    x_table.upsert_to_list('100003.SSZ', 'reason7', 'comments7')
    x_table.upsert_to_list('100003.SSZ', 'reason8', 'comments8')
    x_table.upsert_to_list('100004.SSZ', 'reason8', 'comments8')
    x_table.flush()

    x_table.clear()
    x_table.reload()

    df = x_table.get_name_table()
    assert len(df) == 5


def test_entry():
    test_basic()


# ----------------------------------------------------- File Entry -----------------------------------------------------

def main():
    test_entry()

    # If program reaches here, all test passed.
    print('All test passed.')


# ------------------------------------------------- Exception Handling -------------------------------------------------

def exception_hook(type, value, tback):
    # log the exception here
    print('Exception hook triggered.')
    print(type)
    print(value)
    print(tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)


sys.excepthook = exception_hook


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass
