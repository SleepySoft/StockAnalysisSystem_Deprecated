import logging

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import Utiltity.common as common
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
    from DataHub.UniversalDataCenter import UniversalDataTable
    from DataHub.UniversalDataCenter import UniversalDataCenter
except Exception as e:
    sys.path.append(root_path)

    import Utiltity.common as common
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
    from DataHub.UniversalDataCenter import UniversalDataTable
    from DataHub.UniversalDataCenter import UniversalDataCenter
finally:
    logger = logging.getLogger('')


class DataHubEntry:
    def __init__(self, database_entry: DatabaseEntry, collector_plugin: PluginManager):
        self.__database_entry = database_entry
        self.__collector_plugin = collector_plugin
        self.__data_center = UniversalDataCenter(database_entry, collector_plugin)
        self.build_data_table()

    def get_data_center(self) -> UniversalDataCenter:
        return self.__data_center

    def build_data_table(self):
        table_list = [
            UniversalDataTable('Finance.BalanceSheet', self.__database_entry, 'StockAnalysisSystem'),
            UniversalDataTable('Finance.IncomeStatement', self.__database_entry, 'StockAnalysisSystem'),
            UniversalDataTable('Finance.CashFlowStatement', self.__database_entry, 'StockAnalysisSystem'),

            UniversalDataTable('Marker.TradeCalender', self.__database_entry, 'StockAnalysisSystem',
                               identity_field='exchange', datetime_field='trade_date'),
            UniversalDataTable('Marker.SecuritiesInfo', self.__database_entry, 'StockAnalysisSystem',
                               identity_field='code', datetime_field=None),
        ]
        for table in table_list:
            self.get_data_center().register_data_table(table)



























        # self.__finance_data = FinanceData(collector_plugin, database_entry.get_update_table())
        # self.__trade_calendar = TradeCalendar(collector_plugin, database_entry.get_update_table())
        # self.__securities_info = SecuritiesInfo(collector_plugin, database_entry.get_update_table())
        #
        # database_entry.get_alias_table().register_participant(self.__finance_data)

    # def get_finance_data(self):
    #     return self.__finance_data
    #
    # def get_trade_calendar(self):
    #     return self.__trade_calendar
    #
    # def get_securities_info(self):
    #     return self.__securities_info
