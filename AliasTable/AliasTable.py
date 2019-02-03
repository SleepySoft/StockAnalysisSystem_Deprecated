#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/08/08
@file: AliasTable.py
@function:
@modify:
"""


import json
import numpy as np
import pandas as pd

import public.common
from Database.Database import Database


class AliasTable:
    ALIASES_TABLE = 'AliasTable'
    ALIASES_TABLE_FIELD = ['aliases_name', 'standard_name']

    def __init__(self):
        self.__standard_name_list = []
        self.__aliases_standard_table = {}

    def Init(self, auto: bool) -> bool:
        if auto:
            if not self.LoadFromDB():
                print('Error: Load Aliases Table Fail!')
                return False
        return True

    def Reset(self):
        self.__standard_name_list = []
        self.__aliases_standard_table = {}

    def AddAlias(self, aliases_name: str, standard_name: str):
        if standard_name == '' and aliases_name == '':
            return
        if standard_name != '' and standard_name not in self.__standard_name_list:
            self.__standard_name_list.append(standard_name)
        if aliases_name != '':
            self.__aliases_standard_table[aliases_name] = standard_name

    def DelAlias(self, alias_name: str):
        if alias_name == '' or alias_name not in self.__aliases_standard_table.keys():
            return
        del self.__aliases_standard_table[alias_name]

    def DelStandardName(self, standard_name: str):
        for alias in self.__aliases_standard_table.keys():
            if self.__aliases_standard_table[alias] == standard_name:
                self.__aliases_standard_table[alias] = ''
        if standard_name in self.__standard_name_list:
            self.__standard_name_list.remove(standard_name)

    def UpdateStandardName(self, standard_name: str, standard_name_new: str):
        for alias in self.__aliases_standard_table.keys():
            if self.__aliases_standard_table[alias] == standard_name:
                self.__aliases_standard_table[alias] = standard_name_new
        if standard_name in self.__standard_name_list:
            self.__standard_name_list.remove(standard_name)
            self.__standard_name_list.append(standard_name_new)

    def Standardize(self, name: list or str) -> list or str:
        if isinstance(name, str):
            return self.__do_standardize(name)
        elif isinstance(name, list):
            return [self.__do_standardize(n) for n in name]
        return None

    def GetStandardName(self, name: str) -> str:
        if name in self.__standard_name_list:
            return name
        return self.__aliases_standard_table.get(name, '')

    def GetAliasStandardTable(self) -> dict:
        return self.__aliases_standard_table

    def GetStandardNameList(self) -> list:
        return self.__standard_name_list

    def GetUncategorizedNameList(self) -> list:
        tmp_list = []
        for key in self.__aliases_standard_table.keys():
            if self.__aliases_standard_table[key] == '':
                tmp_list.append(key)
        return tmp_list

    # --------------------------------------------------- Load/Save ---------------------------------------------------

    def LoadFromDB(self) -> bool:
        self.Reset()
        tmp_list = Database().GetUtilityDB().ListFromDB(
            AliasTable.ALIASES_TABLE, AliasTable.ALIASES_TABLE_FIELD)
        if tmp_list is None or len(tmp_list) == 0:
            return False
        for alias, standard in tmp_list:
            self.AddAlias(alias, standard)
        return True

    def DumpToDB(self) -> bool:
        tmp_list = []
        for alias in self.__aliases_standard_table.keys():
            standard = self.__aliases_standard_table[alias]
            tmp_list.append(alias)
            tmp_list.append(standard)
        Database().GetUtilityDB().ListToDB(
            AliasTable.ALIASES_TABLE, tmp_list, -1, 2,
            AliasTable.ALIASES_TABLE_FIELD)
        return True

    def LoadFromCsv(self, file_name: str, replace: bool=True):
        df = pd.read_csv(file_name, header=0)
        column_aliases_name = df['Alias Name']
        column_standard_name = df['Standard Name']
        for alias, standard in zip(column_aliases_name, column_standard_name):
            self.AddAlias(self.__trim_name(alias), standard)
        return True

    def DumpToCsv(self, file_name: str) -> str:
        tmp_list = []
        for k in self.__aliases_standard_table.keys():
            tmp_list.append(k)
            aliases = self.__aliases_standard_table.get(k, [])
            tmp_list.append('|'.join(aliases))
        for n in self.__uncategorized_name_list:
            tmp_list.append('-')
            tmp_list.append(n)
        df = pd.DataFrame(np.array(tmp_list).reshape(-1, 2))
        df.columns = ['standard_name', 'aliases_name']
        try:
            df.to_csv(file_name, encoding='utf_8_sig')
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            pass

    # -----------------------------------------------------------------------------------------

    def __do_standardize(self, name: str):
        alias_name = self.__trim_name(name)
        standard_name = self.GetStandardName(mame_t)
        if standard_name == '':
            self.AddAlias(standard_name, '')
            self.DumpToDB()
        return standard_name

    def __trim_name(self, name: str) -> str:
        name = name.strip()
        name = self.__trim_space(name)
        name = self.__trim_unit(name)
        return name

    def __trim_space(self, name) -> str:
        TRIM_LIST = [' ']
        return self.__list_trim(name, TRIM_LIST)

    def __trim_unit(self, name: str) -> str:
        # How to make it better? Regex? Semantic Analysis?
        TRIM_LIST = ['(万元)', '（万元）']
        return self.__list_trim(name, TRIM_LIST)

    @staticmethod
    def __list_trim(name: str, trim_list: [str]) -> str:
        for t in trim_list:
            name = name.replace(t, '')
        return name

    # ----------------------------------------- Cache for Quick Indexing -----------------------------------------

    def __find_alias(self, alias_name: str) -> str:
        pass


















    # --------------------------------------------------- Build ---------------------------------------------------

    # def RebuildTable(self):
    #     self.__aliases_standard_table.clear()
    #     self.__aliases_standard_table.clear()
    #     self.__update_from_internet()
    #     # self.__update_from_local()
    #     return self.SaveTable()

    def __update_from_internet(self) -> bool:
        df = self.__fetch_standard_table()
        if '英文表达法' not in df.columns and '会计科目名称' not in df.columns:
            print('Cannot find the column in web.')
            return False
        column_aliases_name = df['英文表达法']
        column_standard_name = df['会计科目名称']
        for s, a in zip(column_standard_name, column_aliases_name):
            self.__add_aliases(self.__trim_name(s), a)
        return True

    def __update_from_local(self) -> bool:
        df = pd.read_csv('public/NameTable.csv', header=0)
        column_aliases_name = df['英文']
        column_standard_name = df['中文']
        for s, a in zip(column_standard_name, column_aliases_name):
            self.__add_aliases(self.__trim_name(s), a)
        return True

    @staticmethod
    def __fetch_standard_table() -> pd.DataFrame:
        # From baike.baidu.com
        soup = public.common.GetWebAsSoap(
            'https://baike.baidu.com/item/%E4%BC%9A%E8%AE%A1%E7%A7%91%E7%9B%AE%E4%B8%AD%E8%8B%B1%E6%96%87%E5%AF%B9%E7%85%A7%20%EF%BC%88%E5%8C%97%E4%BA%AC%E5%B8%82%E5%AE%A1%E8%AE%A1%E5%B1%80%E5%8F%91%E5%B8%83%EF%BC%89',
            'utf-8')
        table = soup.find('table', {'log-set-param': 'table_view'})
        if table is None:
            return None

        tr_list = table.findAll('tr')
        if len(tr_list) == 0:
            return None

        df_list = []
        for tr in tr_list:
            tmp_list = []
            td_list = tr.findAll('td')
            if len(td_list) != 5:
                continue
            for td in td_list:
                div = td.find('div')
                if div is not None:
                    tmp_list.append(div.string.strip())
                else:
                    tmp_list.append('')
            df_list.extend(tmp_list)

        df = pd.DataFrame(np.array(df_list).reshape(-1, 5))
        df.columns = df.iloc[0]
        df = df[1:]

        # print(df)
        return df


