#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2019/02/02
@file: ColumnTable.py
@function:
@modify:
"""


import pandas as pd
from Database.Database import Database
from MappingTable.ColumnTable import ColumnTable


class FlexibleTable:
    def __init__(self, table_name: str, fixed_columns: [(str, str)], column_table: ColumnTable,
                 cell_capacity: int, column_reserved: int):
        self.__table_name = table_name
        self.__columnTable = column_table

        self.__fixed_columns = fixed_columns
        self.__flexible_columns = [[str(index), 'varchar(' + str(cell_capacity) + ')'] for index in range(0, column_reserved)]
        self.__field_desc = []
        self.__field_desc.extend(self.__fixed_columns)
        self.__field_desc.extend(self.__flexible_columns)

        self.__cache_table = pd.DataFrame()

    def UpdateTable(self, df: pd.DataFrame, on_column: str):
        pass

    def RemoveColumn(self, df: pd.DataFrame, on_column: str):
        pass
















