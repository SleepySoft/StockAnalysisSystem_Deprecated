#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/08/08
@file: aliases_table.py
@function:
@modify:
"""


import json
import numpy as np
import pandas as pd

import public.common
import stock_analysis_system as sAs


# 20170911: We don't have to use a english name as standard name.
#           Just choose one name as standard. And normalize to it.

class AliasesTable:
    ALIASES_TABLE = 'AliasesTable'
    ALIASES_TABLE_FIELD = ['standard_name', 'aliases_name']

    def __init__(self):
        self.__standard2aliases_table = {}
        self.__aliases2standard_table = {}
        self.__uncategorized_name_list = []

    def Init(self) -> bool:
        if not self.LoadTable() and not self.RebuildTable():
            print('Error: Aliases Table Load Fail!')
            return False
        return True

    # def Readablize(self, name: list or str) -> list or str:
    #     if isinstance(name, str):
    #         return self.__do_readablize(name)
    #     elif isinstance(name, list):
    #         return [self.__do_readablize(n) for n in name]
    #     return None

    def Standardize(self, name: list or str) -> list or str:
        if isinstance(name, str):
            return self.__do_standardize(name)
        elif isinstance(name, list):
            return [self.__do_standardize(n) for n in name]
        return None

    # def GetDefaultName(self, name: str) -> str:
    #     name = self.GetStandardName(name)
    #     if name in self.__standard2default_table:
    #         return self.__standard2default_table.get(name, '')
    #     if name in self.__standard2aliases_table:
    #         aliases_list = self.__standard2aliases_table.get(name, [])
    #         if len(aliases_list) != 0:
    #             return aliases_list[0]
    #     return ''

    def GetStandardName(self, name: str) -> str:
        if name in self.__standard2aliases_table.keys():
            return name
        return self.__aliases2standard_table.get(name, '')

    def GetAliasesNames(self, name: str) -> [str]:
        name = self.__aliases2standard_table.get(name, name)
        return self.__standard2aliases_table.get(name, [])

    def GetUncategorizedNameList(self) -> list:
        return self.__uncategorized_name_list

    # -----------------------------------------------------------------------------------------

    # def __do_readablize(self, name: str):
    #     s_name = self.GetDefaultName(name)
    #     if s_name != '':
    #         return s_name
    #     return name

    # Record the names who didn't have standard name yet.
    def __do_standardize(self, name: str):
        mame_t = self.__trim_name(name)
        name_s = self.GetStandardName(mame_t)
        if name_s != '':
            return name_s
        if mame_t not in self.__uncategorized_name_list:
            self.__uncategorized_name_list.append(mame_t)
            sAs.GetInstance.GetNameTableDB().ExecuteInsertInto(
                AliasesTable.ALIASES_TABLE,
                {
                    AliasesTable.ALIASES_TABLE_FIELD[0]: '',
                    AliasesTable.ALIASES_TABLE_FIELD[1]: json.dumps([mame_t, ])
                 })
        return mame_t

    def __trim_name(self, name: str) -> str:
        name = name.strip()
        name = self.__trim_space(name)
        name = self.__trim_unit(name)
        return name

    def __trim_space(self, name) -> str:
        TRIM_LIST = [
            ' '
        ]
        return self.__list_trim(name, TRIM_LIST)

    def __trim_unit(self, name: str) -> str:
        # How to make it better? Regex? Semantic Analysis?
        TRIM_LIST = [
            '(万元)', '（万元）'
        ]
        return self.__list_trim(name, TRIM_LIST)

    @staticmethod
    def __list_trim(name: str, trim_list: [str]) -> str:
        for t in trim_list:
            name = name.replace(t, '')
        return name

    # --------------------------------------------------- Load/Save ---------------------------------------------------

    def LoadTable(self) -> bool:
        tmp_list = sAs.GetInstance.GetNameTableDB().ListFromDB(
            AliasesTable.ALIASES_TABLE, AliasesTable.ALIASES_TABLE_FIELD)
        if tmp_list is None or len(tmp_list) == 0:
            return False
        for s, aj in tmp_list:
            if len(aj) == 0:
                print('LoadTable() - Error: aj == 0')
                continue
            al = json.loads(aj)
            if len(s) != 0:
                for a in al:
                    self.__add_aliases(s, a)
            else:
                if len(al) > 0:
                    self.__uncategorized_name_list.append(al[0])
        return True

    def SaveTable(self) -> bool:
        tmp_list = []
        for k in self.__standard2aliases_table.keys():
            tmp_list.append(k)
            tmp_list.append(json.dumps(self.__standard2aliases_table.get(k, '')))
        for n in self.__uncategorized_name_list:
            tmp_list.append('')
            tmp_list.append(json.dumps([n, ]))
        sAs.GetInstance.GetNameTableDB().ListToDB(
            AliasesTable.ALIASES_TABLE, tmp_list, -1, 2,
            AliasesTable.ALIASES_TABLE_FIELD)
        return True

        # tmp_list = []
        # for k in self.__aliases2standard_table:
        #     tmp_list.append(k)
        #     tmp_list.append(self.__aliases2standard_table.get(k))
        # sAs.GetInstance.GetNameTableDB().ListToDB('aliases2standard', tmp_list, -1, 2, ['aliases', 'standard'])

    def ExportTable(self, file_name: str) -> str:
        tmp_list = []
        for k in self.__standard2aliases_table.keys():
            tmp_list.append(k)
            aliases = self.__standard2aliases_table.get(k, [])
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

    # --------------------------------------------------- Build ---------------------------------------------------

    def RebuildTable(self):
        self.__standard2aliases_table.clear()
        self.__aliases2standard_table.clear()
        self.__update_from_internet()
        # self.__update_from_local()
        return self.SaveTable()

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

    # ----------------------------------------- Cache for Quick Indexing -----------------------------------------

    def __add_aliases(self, standard_name: str, aliases_name: str):
        if standard_name == '' and aliases_name == '':
            return
        if aliases_name == '':
            self.__uncategorized_name_list.append(aliases_name)
            return
        if standard_name == '':
            self.__uncategorized_name_list.append(aliases_name)
            return
        if aliases_name in self.__aliases2standard_table.keys():
            return
        self.__aliases2standard_table[aliases_name] = standard_name
        if self.__standard2aliases_table.get(standard_name, None) is None:
            self.__standard2aliases_table[standard_name] = []
        if aliases_name not in self.__standard2aliases_table[standard_name]:
            self.__standard2aliases_table[standard_name].append(aliases_name)
        if aliases_name in self.__uncategorized_name_list:
            self.__uncategorized_name_list.remove(aliases_name)


