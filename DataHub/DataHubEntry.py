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


NO_SPEC = {
}

# ---------------------------------------- Query ----------------------------------------

QUERY_FIELDS_TRADE_CALENDER = {
    'exchange':     ([str], ['SSE', 'SZSE'], True)
}

# ---------------------------------------- Result ----------------------------------------

RESULT_FIELDS_TRADE_CALENDER = {
    'exchange':     (['str'], ['SSE', 'SZSE'],      True),
    'trade_date':   (['datetime'], [],              True),
    'status':       (['int'], [],                   True),
}

RESULT_FIELDS_SECURITIES_INFO = {
    'code':           (['str'], [],                 True),
    'name':           (['str'], [],                 True),
    'area':           (['str'], [],                 False),
    'industry':       (['str'], [],                 False),
    'fullname':       (['str'], [],                 False),
    'en_name':        (['str'], [],                 False),
    'market':         (['str'], [],                 False),
    'exchange':       (['str'], ['SSE', 'SZSE'],    True),
    'currency':       (['str'], [],                 False),
    'list_status':    (['int'], [],                 False),
    'listing_date':   (['datetime'], [],            False),
    'delisting_date': (['datetime'], [],            False),
    'stock_connect':  (['int'], [],                 False),
}

# ---------------------------------------- Declare ----------------------------------------

DFTDB = 'StockAnalysisSystem'
DFTPRX = ''

DATA_FORMAT_URI = 0
DATA_FORMAT_DATABASE = 1
DATA_FORMAT_TABLE_PREFIX = 2
DATA_FORMAT_IDENTITY_FIELD = 3
DATA_FORMAT_DATETIME_FIELD = 4
DATA_FORMAT_QUERY_FIELD_INFO = 5
DATA_FORMAT_RESULT_FIELD_INFO = 6

DATA_FORMAT_DECLARE = [
    ('Marker.TradeCalender', DFTDB, DFTPRX,  'exchange', 'trade_date',   QUERY_FIELDS_TRADE_CALENDER, NO_SPEC),
    ('Marker.SecuritiesInfo', DFTDB, DFTPRX, 'code',     None,           NO_SPEC, RESULT_FIELDS_SECURITIES_INFO),

    ('Finance.BalanceSheet', DFTDB, DFTPRX,      NO_SPEC, RESULT_FIELDS_SECURITIES_INFO),
    ('Finance.BalanceSheet', DFTDB, DFTPRX,      NO_SPEC, RESULT_FIELDS_SECURITIES_INFO),
    ('Finance.CashFlowStatement', DFTDB, DFTPRX, NO_SPEC, RESULT_FIELDS_SECURITIES_INFO),
]


class DataHubEntry:
    def __init__(self, database_entry: DatabaseEntry, collector_plugin: PluginManager):
        self.__database_entry = database_entry
        self.__collector_plugin = collector_plugin
        self.__data_center = UniversalDataCenter(database_entry, collector_plugin)
        self.build_data_table()

    def get_data_center(self) -> UniversalDataCenter:
        return self.__data_center

    def build_data_table(self):
        for data_format in DATA_FORMAT_DECLARE:
            self.get_data_center().register_data_table(
                UniversalDataTable(data_format[DATA_FORMAT_URI], self.__database_entry,
                                   data_format[DATA_FORMAT_DATABASE], data_format[DATA_FORMAT_TABLE_PREFIX],
                                   data_format[DATA_FORMAT_IDENTITY_FIELD], data_format[DATA_FORMAT_DATETIME_FIELD])
            )



























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
