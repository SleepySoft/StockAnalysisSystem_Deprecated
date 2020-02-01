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
from Utiltity.common import *
from Utiltity.time_utility import *


class StockAnalysisSystem(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.__inited = False
        self.__quit_lock = 0

        self.__collector_plugin = None
        self.__strategy_plugin = None

        self.__data_hub_entry = None
        self.__strategy_entry = None
        self.__database_entry = None

    def can_sys_quit(self) -> bool:
        return self.__quit_lock == 0

    def lock_sys_quit(self):
        self.__quit_lock += 1

    def release_sys_quit(self) -> bool:
        self.__quit_lock = max(0, self.__quit_lock - 1)

    def check_initialize(self) -> bool:
        if self.__inited:
            return True

        clock = Clock()
        print('Initializing Stock Analysis System ...')

        import DataHub.DataHubEntry as DataHubEntry
        import Strategy.StrategyEntry as StrategyEntry
        import Database.DatabaseEntry as DatabaseEntry
        import Utiltity.plugin_manager as plugin_manager

        root_path = path.dirname(path.abspath(__file__))

        self.__strategy_plugin = plugin_manager.PluginManager(path.join(root_path, 'Analyzer'))
        self.__collector_plugin = plugin_manager.PluginManager(path.join(root_path, 'Collector'))

        self.__strategy_plugin.refresh()
        self.__collector_plugin.refresh()

        self.__database_entry = DatabaseEntry.DatabaseEntry(path.join(root_path, 'Data'))
        self.__data_hub_entry = DataHubEntry.DataHubEntry(self.__database_entry, self.__collector_plugin)
        self.__strategy_entry = StrategyEntry.StrategyEntry(self.__strategy_plugin,
                                                            self.__data_hub_entry, self.__database_entry)

        print('Stock Analysis System Initialization Done, Time spending: ' + str(clock.elapsed_ms()) + ' ms')
        self.__inited = True
        return True

    def get_database_entry(self):
        return self.__database_entry if self.check_initialize() else None

    def get_data_hub_entry(self):
        return self.__data_hub_entry if self.check_initialize() else None

    def get_strategy_entry(self):
        return self.__strategy_entry if self.check_initialize() else None






