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

from os import sys, path
import Utiltity.common as common


class StockAnalysisSystem(metaclass=common.ThreadSafeSingleton):
    def __init__(self):
        self.__inited = False

        self.__collector_plugin = None
        self.__strategy_plugin = None

        self.__data_hub_entry = None
        self.__strategy_entry = None
        self.__database_entry = None

    def check_initialize(self) -> bool:
        if self.__inited:
            return True

        import DataHub.DataHubEntry as DataHubEntry
        import Strategy.StrategyEntry as StrategyEntry
        import Database.DatabaseEntry as DatabaseEntry
        import Utiltity.plugin_manager as plugin_manager

        root_path = path.dirname(path.abspath(__file__))

        self.__strategy_plugin = plugin_manager.PluginManager(path.join(root_path, 'Analyzer'))
        self.__collector_plugin = plugin_manager.PluginManager(path.join(root_path, 'Collector'))

        self.__strategy_plugin.refresh()
        self.__collector_plugin.refresh()

        root_path = path.dirname(path.abspath(__file__))

        self.__database_entry = DatabaseEntry.DatabaseEntry(path.join(root_path, 'Data'))
        self.__strategy_entry = StrategyEntry.StrategyEntry(self.__strategy_plugin)
        self.__data_hub_entry = DataHubEntry.DataHubEntry(self.__database_entry, self.__collector_plugin)
        self.__inited = True

        return True

    def get_database_entry(self):
        return self.__database_entry if self.check_initialize() else None

    def get_data_hub_entry(self):
        return self.__data_hub_entry if self.check_initialize() else None

    # ------------------------------------ private ------------------------------------

    def __check_init_status(self, expected: bool) -> bool:
        if self.__inited != expected:
            if self.__inited:
                print('System has been inited.')
            else:
                print('System not been inited yet.')
            return False
        return True


instance = StockAnalysisSystem()
