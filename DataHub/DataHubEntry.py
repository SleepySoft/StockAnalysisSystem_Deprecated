import logging

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import Utiltity.common as common

    from DataHub.finance_data import FinanceData
    from DataHub.trade_calendar import TradeCalendar
    from DataHub.securities_info import SecuritiesInfo

    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    import Utiltity.common as common

    from DataHub.finance_data import FinanceData
    from DataHub.trade_calendar import TradeCalendar
    from DataHub.securities_info import SecuritiesInfo

    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
finally:
    logger = logging.getLogger('')


class DataHubEntry(metaclass=common.ThreadSafeSingleton):
    def __init__(self, database_entry: DatabaseEntry = None, collector_plugin: PluginManager = None):
        if database_entry is None:
            database_entry = DatabaseEntry()
        if collector_plugin is None:
            plugin_path = root_path + '/Collector/'
            collector_plugin = PluginManager(plugin_path)
            collector_plugin.refresh()

        self.__finance_data = FinanceData(collector_plugin, database_entry.get_update_table())
        self.__trade_calendar = TradeCalendar(collector_plugin, database_entry.get_update_table())
        self.__securities_info = SecuritiesInfo(collector_plugin, database_entry.get_update_table())

    def get_finance_data(self):
        return self.__finance_data

    def get_trade_calendar(self):
        return self.__trade_calendar

    def get_securities_info(self):
        return self.__securities_info
