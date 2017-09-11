#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:YuQiu
@time: 2017/08/08
@file: stock_analysis_system.py
@function:
@modify:
"""

import public.db_access
import public.aliases_table


class StockAnalysisSystem:
    def __init__(self):
        self.__inited = False
        self.__initing = False
        self.__db_plug_in = None
        self.__db_name_table = None
        self.__db_data_center = None
        self.__aliases_table = None
        self.__component_data_center = None
        self.__component_data_collector = None
        self.__component_strategy_manager = None

    def Init(self) -> bool:
        if not self.__check_init(False):
            return True
        self.__initing = True

        self.__db_plug_in = public.db_access.DBAccess()
        self.__db_name_table = public.db_access.DBAccess()
        self.__db_data_center = public.db_access.DBAccess()
        self.__aliases_table = public.aliases_table.AliasesTable()

        import data_center
        import data_collector
        import strategy_manager

        self.__component_data_center = data_center.DataCenter()
        self.__component_data_collector = data_collector.DataCollector()
        self.__component_strategy_manager = strategy_manager.StrategyManager()

        result = True
        result = self.__db_plug_in.Init('Data/Plug-in.db') and result
        result = self.__db_name_table.Init('Data/NameTable.db') and result
        result = self.__db_data_center.Init('Data/DataCenter.db') and result
        result = self.__aliases_table.Init() and result                         # Depends on __db_name_table
        result = self.__component_data_center.Init() and result                 # Depends on __db_data_center
        result = self.__component_data_collector.Init() and result
        result = self.__component_strategy_manager.Init() and result

        self.__inited = True
        self.__initing = False

        return result

    def GetPluginDB(self) -> public.db_access.DBAccess:
        self.__check_init(True)
        return self.__db_plug_in

    def GetNameTableDB(self) -> public.db_access.DBAccess:
        self.__check_init(True)
        return self.__db_name_table

    def GetDataCenterDB(self) -> public.db_access.DBAccess:
        self.__check_init(True)
        return self.__db_data_center

    def GetAliasesTable(self) -> public.aliases_table.AliasesTable:
        self.__check_init(True)
        return self.__aliases_table

    def GetDataCenter(self):
        self.__check_init(True)
        return self.__component_data_center

    def GetStrategyManager(self):
        self.__check_init(True)
        return self.__component_strategy_manager

    def GetDataCollector(self):
        self.__check_init(True)
        return self.__component_data_collector

    # ------------------------------------ private ------------------------------------

    def __check_init(self, expected: bool) -> bool:
        if not self.__initing and self.__inited != expected:
            if self.__inited:
                print('System has been inited.')
            else:
                print('System not been inited yet.')
            return False
        return True

GetInstance = StockAnalysisSystem()
