import traceback
import pandas as pd

from os import sys, path
import datetime
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    from DataHub.DataUtility import DataUtility
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
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Utiltity.plugin_manager import PluginManager
    from Database.Database import Database
    from Database.DataTable import DataTable
    from Database.UpdateTable import UpdateTable
    from Utiltity.plugin_manager import PluginManager
finally:
    pass


NEED_COLLECTOR_CAPACITY = [
    'TradeCalender',
    'SecuritiesInfo',
    'IndexComponent',
]

SECURITIES_SH = 0x01
SECURITIES_SZ = 0x02
SECURITIES_A_SHARES = SECURITIES_SH & SECURITIES_SZ

TABLE_TRADE_CALENDER = 'TradeCalender'
FIELD_TRADE_CALENDER = ['exchange', 'trade_date', 'status']

TRADE_EXCHANGE = ['SSE', 'SZSE']


class TradeCalendar(DataUtility):
    def __init__(self, plugin: PluginManager, update: UpdateTable):
        super().__init__(plugin, update)
        self.__cached_data = {}
        self.__load_cached_data()

    # --------------------------------------------------- Interface ---------------------------------------------------

    def need_update(self, tags: [str]) -> DataUtility.RESULT_CODE:
        latest_update = self._get_data_last_update(['TradeCalender', '', ''])
        return latest_update != yesterday()

    def execute_update(self, tags: [str]) -> DataUtility.RESULT_CODE:
        for exchange in TRADE_EXCHANGE:
            since, until = self.get_cached_data_range(tags)
            if until is None:
                since = datetime.datetime(1990, 1, 1)
                until = today()
            elif until == yesterday():
                continue
            else:
                since = until
                until = today()
            df = self.__do_fetch_trade_calender(exchange, since, until)
            if df is None:
                continue
            exists_df = self.__cached_data.get(exchange)
            if exists_df is not None:
                self.__cached_data[exchange] = concat_dataframe_by_index([exists_df, df])
            else:
                self.__cached_data[exchange] = df

    # --------------------------------------------------- private if ---------------------------------------------------

    def data_from_cache(self, tags: [str],
                        timeval: (datetime.datetime, datetime.datetime),
                        extra: dict = None) -> pd.DataFrame:
        if not self.is_data_support(tags):
            return None
        df = self.__cached_data.get(tags[0])
        if df is None:
            return None
        if len(timeval) > 0 and timeval[0] is not None:
            df = df[df['trade_date'] >= timeval[0]]
        if len(timeval) > 1 and timeval[1] is not None:
            df = df[df['trade_date'] <= timeval[1]]
        return df

    # -------------------------------------------------- probability --------------------------------------------------

    def get_root_tags(self) -> [str]:
        return TRADE_EXCHANGE

    def is_data_support(self, tags: [str]) -> bool:
        return len(tags) > 1 and tags[0] in TRADE_EXCHANGE

    def get_cached_data_range(self, tags: [str]) -> (datetime.datetime, datetime.datetime):
        if not self.is_data_support(tags):
            return None, None
        df = self.__cached_data.get(tags[0])
        if df is None:
            return None, None
        min_date = min(df['trade_date'])
        max_date = max(df['trade_date'])
        return min_date, max_date

    # def get_cache_last_update(self, tags: [str]) -> datetime.datetime:
    #     _tags = self.__normalize_tags(tags)
    #     return self.get_update_table().update_latest_update_time(*_tags)

    # ---------------------------------------------------- private -----------------------------------------------------

    def __do_fetch_trade_calender(self, exchange: str, since: datetime.datetime, until: datetime.datetime):
        plugins = self.get_plugin_manager().find_module_has_capacity('TradeCalender')
        for plugin in plugins:
            df = self.get_plugin_manager().execute_module_function(plugin, 'fetch_data', {
                'content': 'TradeCalender',
                'exchange': exchange,
                'since': since,
                'until': until,
            })
            if df is None or len(df) == 0:
                continue
            continuity, min_date, max_date = check_date_continuity(df, 'trade_date')
            if not continuity:
                continue
            if min_date < since:
                df = df.loc[df['trade_date'] >= since]
            return df
        return None

    def __load_cached_data(self) -> bool:
        df = Database().get_utility_db().DataFrameFromDB('TradeCalender', FIELD_TRADE_CALENDER)
        if df is None:
            df = pd.DataFrame(columns=FIELD_TRADE_CALENDER)
        for exchange in TRADE_EXCHANGE:
            self.__cached_data[exchange] = df[df['exchange'] == exchange]
        return True

    def __save_cached_data(self) -> bool:
        return Database().get_utility_db().DataFrameToDB('TradeCalender', self.__cached_data)


# ----------------------------------------------------- Test Code ------------------------------------------------------


def __build_instance() -> TradeCalendar:
    from os import path
    root_path = path.dirname(path.dirname(path.abspath(__file__)))
    plugin_path = root_path + '/Collector/'

    collector_plugin = PluginManager(plugin_path)
    collector_plugin.refresh()

    update_table = UpdateTable()

    return TradeCalendar(collector_plugin, update_table)


def test_basic_feature():
    md = __build_instance()
    md.query_data('SSE')


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










