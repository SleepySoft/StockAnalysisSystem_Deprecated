#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/08/08
@file: db_access.py
@function:
@modify:
"""


import sqlite3
import traceback
import numpy as np
import pandas as pd


class DBAccess:

    def __init__(self):
        self.__db_name = ''

    def Init(self, db_name: str, user = '', passwd = '', extra = '') -> bool:
        self.__db_name = db_name
        return True

    # ----------------------------------- connection and cursor -----------------------------------

    def BuildConnection(self) -> sqlite3.Connection:
        if len(self.__db_name) == 0:
            return None
        try:
            return sqlite3.connect(self.__db_name)
        except Exception as e:
            print('Error =>', e)
            print('Error =>', traceback.format_exc())
            return None
        finally:
            pass

    def BuildConnectionCursor(self) -> (sqlite3.Connection, sqlite3.Cursor):
        connection = self.BuildConnection()
        if connection is None:
            return None, None
        cursor = connection.cursor()
        if cursor is None:
            connection.close()
            return None, None
        return connection, cursor

    # ----------------------------------- Safe Execute -----------------------------------

    # Data Description Language: Table
    def SafeExecuteDDL(self, sql_ddl: str, connection: sqlite3.Connection) -> bool:
        if connection is None:
            return False
        try:
            connection.execute(sql_ddl)
            connection.commit()
        except Exception as e:
            print('Error =>', e)
            print('Error =>', traceback.format_exc())
            return False
        finally:
            pass
        return True

    # Data Manipulation Language: SELECT, UPDATE, DELETE, INSERT INTO
    def SafeExecuteDML(self, sql_dml: str, cursor: sqlite3.Cursor) -> bool:
        if cursor is None:
            return False
        try:
            cursor.execute(sql_dml)
        except Exception as e:
            print('Error =>', e)
            print('Error =>', traceback.format_exc())
            return False
        finally:
            pass
        return True

    # ----------------------------------- Quick Execute -----------------------------------

    def QuickExecuteDDL(self, sql_ddl: str) -> bool:
        connection = self.BuildConnection()
        if connection is not None:
            ret = self.SafeExecuteDDL(sql_ddl, connection)
            connection.close()
            return ret
        return False

    def QuickExecuteDML(self, sql_dml: str, commit: bool = False) -> bool:
        connection, cursor = self.StartExecuteDML(sql_dml)
        if cursor is None and connection is None:
            return False
        if commit:
            connection.commit()
        cursor.close()
        connection.close()
        return True

    def StartExecuteDML(self, sql_dml: str) -> (sqlite3.Connection, sqlite3.Cursor):
        connection, cursor = self.BuildConnectionCursor()
        if cursor is None:
            return None, None
        try:
            cursor.execute(sql_dml)
        except Exception as e:
            print('Error =>', e)
            print('Error =>', traceback.format_exc())
            cursor.close()
            connection.close()
            return None, None
        finally:
            pass
        return connection, cursor

    # ----------------------------------- Advance DDL -----------------------------------

    def TableExists(self, table_name: str) -> bool:
        sql = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + table_name + "'"
        connection, cursor = self.StartExecuteDML(sql)

        if cursor is None:
            return False
        b = cursor.fetchall()
        existence = (b[0][0] == 1)

        cursor.close()
        connection.close()
        return existence

    def CreateTable(self, table_name: str, table_desc: [[str, str]]) -> bool:
        fields = ''
        for pair in table_desc:
            if len(pair) < 2:
                return False
            if fields != '':
                fields += ', '
            fields += pair[0] + ' ' + pair[1]
        sql = 'CREATE TABLE IF NOT EXISTS ' + table_name + ' (' + fields + ');'
        return self.QuickExecuteDDL(sql)

    def DropTable(self, table_name) -> bool:
        return self.QuickExecuteDDL('DROP TABLE ' + table_name)

    # ----------------------------------- Advance DML -----------------------------------

    def ExecuteSelect(self, table_name: str, columns: [str], condition: str = '') -> (sqlite3.Connection, sqlite3.Cursor):
        sql = self.__gen_sql_select(table_name, columns, condition)
        return self.StartExecuteDML(sql)

    def ExecuteUpdate(self, table_name: str, update_column: map, condition: str = '') -> bool:
        sql = self.__gen_sql_update(table_name, update_column, condition)
        return self.QuickExecuteDML(sql, True)

    # For safety, condition is required.
    def ExecuteDelete(self, table_name: str, condition: str) -> bool:
        if condition == '':
            return False
        sql = 'DELETE FROM ' + table_name + ' WHERE ' + condition
        return self.QuickExecuteDML(sql, True)

    def ExecuteInsertInto(self, table_name: str, insert_column: map) -> bool:
        sql = self.__gen_sql_insert_into(table_name, insert_column)
        return self.QuickExecuteDML(sql, True)

    def ExecuteUpdateOrInsert(self, table_name: str, insert_column: map, key_columns: [str]) -> bool:
        sql = 'INSERT OR IGNORE INTO ' + table_name
        columns, values = self.__gen_insert_pairs(insert_column)
        sql += ' (' + columns + ') VALUES (' + values + ');'
        condition = ''
        for c in key_columns:
            if c not in insert_column.keys():
                return False
            if condition != '':
                condition += ' AND '
            condition += c + " = '" + insert_column.get(c, '') + "'"
        sql += self.__gen_sql_update(table_name, insert_column, condition)
        return self.QuickExecuteDML(sql, True)

    # ----------------------------------- Structure Write -----------------------------------

    def ListToDB(self, table_name: str, list_: list, rows: int, cols: int, columns: [str] = None) -> bool:
        df = pd.DataFrame(np.array(list_).reshape(rows, cols))
        if columns is not None:
            df.columns = columns
        return self.DataFrameToDB(table_name, df)

    def DataFrameToDB(self, table_name: str, df: pd.DataFrame, if_exists: str = 'replace') -> bool:
        connection, cursor = self.BuildConnectionCursor()
        if cursor is None:
            return False
        try:
            df.to_sql(table_name, connection, flavor='sqlite', if_exists='replace', index=True)
        except Exception as e:
            print(e)
            return False
        finally:
            connection.commit()
            cursor.close()
            connection.close()
        return True

    # ----------------------------------- Structure Read -----------------------------------

    def ListFromDB(self, table_name: str, columns: [str], condition: str = '') -> [()]:
        connection, cursor = self.ExecuteSelect(table_name, columns, condition)
        if cursor is None:
            return None
        values = cursor.fetchall()
        cursor.close()
        connection.close()
        return values

    def DataFrameFromDB(self, table_name: str, columns: [str] = [], condition: str = '') -> pd.DataFrame:
        sql = self.__gen_sql_select(table_name, columns, condition)
        connection = self.BuildConnection()
        if connection is None:
            return None
        try:
            return pd.read_sql_query(sql, connection)
        except Exception as e:
            print(e)
        finally:
            connection.close()
        return None

    # ============================================ File operation  ============================================

    def ExportTable(self, table_name: str, file_name: str) -> bool:
        df = self.DataFrameFromDB(table_name)
        if df is None:
            return
        df.to_csv(file_name)
        return True

    # ============================================ Generate SQL  ============================================

    def __gen_sql_select(self, table_name: str, columns: [str], condition: str = '') -> str:
        if columns is None or len(columns) == 0:
            sql = 'select * from ' + table_name
        else:
            sql = 'select ' + ', '.join(columns) + ' from ' + table_name
        if len(condition) != 0:
            sql += ' where ' + condition
        return sql

    def __gen_sql_update(self, table_name: str, update_column: map, condition: str = '') -> str:
        if update_column is None or len(update_column) == 0:
            return ''
        sql = 'UPDATE ' + table_name + ' SET '
        sql += self.__gen_update_pairs(update_column)
        if condition != '':
            sql += ' WHERE ' + sql
        return sql

    def __gen_sql_insert_into(self, table_name: str, insert_column: map) -> str:
        if insert_column is None or len(insert_column) == 0:
            return ''
        columns, values = self.__gen_insert_pairs(insert_column)
        return 'INSERT INTO ' + table_name + ' (' + columns + ') VALUES (' + values + ')'

    def __gen_update_pairs(self, update_column: map) -> str:
        sql = ''
        for k in update_column.keys():
            sql += k + " = '" + update_column.get(k) + "', "
        if sql.endswith(', '):
            sql = sql[0:-2]
        return sql

    def __gen_insert_pairs(self, insert_column: map) -> (str, str):
        columns = values = ''
        for k in insert_column.keys():
            columns += k + ', '
            values += "'" + insert_column.get(k) + "', "
        if columns.endswith(', '):
            columns = columns[0:-2]
        if values.endswith(', '):
            values = values[0:-2]
        return columns, values





