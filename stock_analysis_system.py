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
        self.__log_errors = []

        import config
        self.__config = config.Config()

        self.__collector_plugin = None
        self.__strategy_plugin = None

        self.__data_hub_entry = None
        self.__strategy_entry = None
        self.__database_entry = None

    # -------------------------------------- Quit Lock --------------------------------------

    def can_sys_quit(self) -> bool:
        return self.__quit_lock == 0

    def lock_sys_quit(self):
        self.__quit_lock += 1

    def release_sys_quit(self) -> bool:
        self.__quit_lock = max(0, self.__quit_lock - 1)

    # ---------------------------------------- Config ----------------------------------------

    def get_config(self):
        return self.__config

    def get_log_errors(self) -> [str]:
        return self.__log_errors

    # ----------------------------------------- Init -----------------------------------------

    def is_initialized(self) -> bool:
        return self.__inited

    def check_initialize(self) -> bool:
        if self.__inited:
            return True

        print('Initializing Stock Analysis System ...')

        clock = Clock()
        self.__log_errors = []
        root_path = path.dirname(path.abspath(__file__))

        import DataHub.DataHubEntry as DataHubEntry
        import Strategy.StrategyEntry as StrategyEntry
        import Database.DatabaseEntry as DatabaseEntry
        import Utiltity.plugin_manager as plugin_manager

        if not self.__config.load_config():
            self.__log_errors.append('Load config fail.')
            return False

        self.__database_entry = DatabaseEntry.DatabaseEntry()

        if not self.__database_entry.config_sql_db(path.join(root_path, 'Data')):
            self.__log_errors.append('Config SQL database fail.')
            return False

        if not self.__database_entry.config_nosql_db(self.__config.get('NOSQL_DB_HOST'),
                                                     self.__config.get('NOSQL_DB_PORT'),
                                                     self.__config.get('NOSQL_DB_USER'),
                                                     self.__config.get('NOSQL_DB_PASS')):
            self.__log_errors.append('Config NoSql database fail.')
            return False

        self.__strategy_plugin = plugin_manager.PluginManager(path.join(root_path, 'Analyzer'))
        self.__collector_plugin = plugin_manager.PluginManager(path.join(root_path, 'Collector'))

        self.__strategy_plugin.refresh()
        self.__collector_plugin.refresh()

        self.__data_hub_entry = DataHubEntry.DataHubEntry(self.__database_entry, self.__collector_plugin)
        self.__strategy_entry = StrategyEntry.StrategyEntry(self.__strategy_plugin,
                                                            self.__data_hub_entry, self.__database_entry)

        print('Stock Analysis System Initialization Done, Time spending: ' + str(clock.elapsed_ms()) + ' ms')
        self.__inited = True
        return True

    # -------------------------------------------- Entry --------------------------------------------

    def get_database_entry(self):
        return self.__database_entry if self.check_initialize() else None

    def get_data_hub_entry(self):
        return self.__data_hub_entry if self.check_initialize() else None

    def get_strategy_entry(self):
        return self.__strategy_entry if self.check_initialize() else None






