import traceback
import pandas as pd

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    from DataHub.DataUtility import DataUtility
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Utiltity.plugin_manager import PluginManager
    from Database.Database import Database
    from Database.DataTable import DataTable
    from Database.UpdateTable import UpdateTable
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    from DataHub.DataUtility import DataUtility
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Utiltity.plugin_manager import PluginManager
    from Database.Database import Database
    from Database.DataTable import DataTable
    from Database.UpdateTable import UpdateTable
    from Utiltity.plugin_manager import PluginManager
finally:
    logger = logging.getLogger('')


NEED_COLLECTOR_CAPACITY = [
    'SecuritiesInfo',
]
SECURITIES_EXCHANGE = ['SSE', 'SZSE']
TABLE_SECURITIES_INFO = 'SecuritiesInfo'
IDENTITY_SECURITIES_INFO = '<stock_code>.<exchange>'
FIELD_INFO = {'code':           (['str'], []),
              'name':           (['str'], []),
              'area':           (['str'], []),
              'industry':       (['str'], []),
              'fullname':       (['str'], []),
              'en_name':        (['str'], []),
              'market':         (['str'], []),
              'exchange':       (['str'], ['SSE', 'SZSE']),
              'currency':       (['str'], []),
              'list_status':    (['int'], []),
              'listing_date':   (['datetime'], []),
              'delisting_date': (['datetime'], []),
              'stock_connect':  (['int'], [])
              }


class SecuritiesInfo(DataUtility):
    def __init__(self, plugin: PluginManager, update: UpdateTable):
        super().__init__(plugin, update)
        self.__cached_data = None
        self.__load_cached_data()

    def execute_single_update(self, tags: [str],
                              timeval: (datetime.datetime, datetime.datetime) = None) -> DataUtility.RESULT_CODE:
        nop(timeval)
        logger.info('SecuritiesInfo.execute_single_update()')
        df = self.__do_fetch_securities_info(tags)
        if df is None or len(df) == 0:
            return DataUtility.RESULT_FAILED
        df.reindex()
        self.__cached_data = df
        return DataUtility.RESULT_SUCCESSFUL

    def execute_batch_update(self) -> DataUtility.RESULT_CODE:
        nop(self)
        logger.info('SecuritiesInfo.execute_batch_update()')
        return self.execute_single_update([])

    def trigger_save_data(self, tags: [str]) -> DataUtility.RESULT_CODE:
        nop(self)
        logger.info('DataUtility.trigger_save_data(' + str(tags) + ') -> RESULT_NOT_IMPLEMENTED')
        return DataUtility.RESULT_NOT_IMPLEMENTED

    def __do_fetch_securities_info(self, tags: [str]) -> pd.DataFrame:
        plugins = self.get_plugin_manager().find_module_has_capacity('SecuritiesInfo')
        for plugin in plugins:
            df = self.get_plugin_manager().execute_module_function(plugin, 'fetch_data', {
                'exchange': tags
            })

            print('-------------------------------------------------------------------------------------------')
            print(df)
            print('-------------------------------------------------------------------------------------------')

            if not self._check_dataframe_field(df, FIELD_INFO, ['code', 'exchange']) or len(df) == 0:
                logger.info('SecuritiesInfo - Fetch data format Error.')
                continue
            return df
        return None

    def __load_cached_data(self) -> bool:
        df = Database().get_utility_db().DataFrameFromDB('TradeCalender', FIELD_TRADE_CALENDER)
        if df is None:
            df = pd.DataFrame(columns=FIELD_TRADE_CALENDER)
        for exchange in TRADE_EXCHANGE:
            self.__cached_data[exchange] = df[df['exchange'] == exchange]
            self.__cached_data[exchange].reindex()
        return True

    def __save_cached_data(self) -> bool:
        first = True
        result = True
        for exchange in self.__cached_data.keys():
            df = self.__cached_data[exchange]
            if df is None or len(df) == 0:
                continue
            if_exists = 'replace' if first else 'append'
            first = False
            if Database().get_utility_db().DataFrameToDB('TradeCalender', df, if_exists):
                self._update_time_record(['TradeCalender', exchange], df, 'trade_date')
            else:
                result = False
        return result


# ----------------------------------------------------- Test Code ------------------------------------------------------


def __build_instance() -> SecuritiesInfo:
    from os import path
    root_path = path.dirname(path.dirname(path.abspath(__file__)))
    plugin_path = root_path + '/Collector/'

    collector_plugin = PluginManager(plugin_path)
    collector_plugin.refresh()

    update_table = UpdateTable()

    return SecuritiesInfo(collector_plugin, update_table)


def test_basic_feature():
    md = __build_instance()
    df = md.query_data('SSE')
    print(df)
    df = md.query_data('SZSE')
    print(df)


def test_entry():
    test_basic_feature()


# ----------------------------------------------------- File Entry -----------------------------------------------------

def main():
    test_entry()

    # If program reaches here, all test passed.
    print('All test passed.')


# ------------------------------------------------- Exception Handling -------------------------------------------------

def exception_hook(type, value, tback):
    # log the exception here
    print('Exception hook triggered.')
    print(type)
    print(value)
    print(tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)


sys.excepthook = exception_hook


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass







