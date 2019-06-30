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
    'FinanceData',
]
TABLE_FINANCE_DATA = 'FinanceData'
IDENTITY_FINANCE_DATA = '<stock_code>.<exchange>'
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


class FinanceData(DataUtility):
    def __init__(self, plugin: PluginManager, update: UpdateTable):
        super().__init__(plugin, update)
        self.__cached_data = None
        self.__load_cached_data()

    # ---------------------------------------------------------------------------------x--------------------------------

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
        result = self.__save_cached_data()
        if result:
            self.get_update_table().update_latest_update_time('SecuritiesInfo', '', '')
            return DataUtility.RESULT_SUCCESSFUL
        return DataUtility.RESULT_FAILED

    # --------------------------------------------------- private if ---------------------------------------------------

    def data_from_cache(self, tags: [str],
                        timeval: (datetime.datetime, datetime.datetime),
                        extra: dict = None) -> pd.DataFrame:
        nop(tags)
        nop(timeval)
        nop(extra)
        return self.__cached_data

    # -------------------------------------------------- probability --------------------------------------------------

    def get_reference_data_range(self, tags: [str]) -> (datetime.datetime, datetime.datetime):
        nop(self, tags)
        return [None, None]

    # -----------------------------------------------------------------------------------------------------------------

    def __do_fetch_finance_data(self, tags: [str]) -> pd.DataFrame:
        pass
        # plugins = self.get_plugin_manager().find_module_has_capacity('SecuritiesInfo')
        # for plugin in plugins:
        #     df = self.get_plugin_manager().execute_module_function(plugin, 'fetch_data', {
        #         'content': 'SecuritiesInfo',
        #         'exchange': tags
        #     })
        #
        #     if not self._check_dataframe_field(df, FIELD_INFO, ['code', 'exchange']) or len(df) == 0:
        #         logger.info('SecuritiesInfo - Fetch data format Error.')
        #         continue
        #     return df
        # return None

    def __load_cached_data(self) -> bool:
        pass
        # table = DataTable().get_securities_table()
        # record = table.query()
        # if record is not None and len(record) > 0:
        #     self.__cached_data = pd.DataFrame(record)
        #     del self.__cached_data['DateTime']
        #     del self.__cached_data['_id']
        # else:
        #     self.__cached_data = pd.DataFrame(column=list(FIELD_INFO.keys()))
        # return True

    def __save_cached_data(self) -> bool:
        pass
        # table = DataTable().get_securities_table()
        # for index, row in self.__cached_data.iterrows():
        #     code = row['code']
        #     exchange = row['exchange']
        #     identity = IDENTITY_SECURITIES_INFO.\
        #         replace('<stock_code>', code).\
        #         replace('<exchange>', exchange)
        #     table.upsert(identity, text_auto_time('2000-01-01'), row.to_dict())
        # return True


# ----------------------------------------------------- Test Code ------------------------------------------------------


def __build_instance() -> FinanceData:
    from os import path
    root_path = path.dirname(path.dirname(path.abspath(__file__)))
    plugin_path = root_path + '/Collector/'

    collector_plugin = PluginManager(plugin_path)
    collector_plugin.refresh()

    update_table = UpdateTable()

    return FinanceData(collector_plugin, update_table)


def test_basic_feature():
    pass


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







