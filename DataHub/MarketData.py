import sys
import traceback
import pandas as pd

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Database.Database import Database
    from Database import UpdateTable
    from Database.DataTable import DataTable
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Database.Database import Database
    from Database import UpdateTable
    from Database.DataTable import DataTable
    from Utiltity.plugin_manager import PluginManager
finally:
    pass


NEED_COLLECTOR_CAPACITY = [
    'TradeCalender',
    'SecuritiesInfo',
    'IndexComponent',
]


class MarketData:
    SECURITIES_SH = 0x01
    SECURITIES_SZ = 0x02
    SECURITIES_A_SHARES = SECURITIES_SH & SECURITIES_SZ

    TABLE_TRADE_CALENDER = 'TradeCalender'
    FIELD_TRADE_CALENDER = ['Exchange', 'TradeDate', 'Status']

    TRADE_EXCHANGE = ['SSE', 'SZSE']

    def __init__(self, plugin: PluginManager):
        self.__plugin = plugin

    # ----------------------------- Gets List -----------------------------

    def get_trade_calender(self, since: datetime = None, until: datetime = None) -> dict:
        pass

    def check_update_trade_calender(self):
        self.__check_update_trade_calender()

    def force_update_trade_calender(self):
        since = datetime(1900, 1, 1)
        until = today()
        self.__do_update_trace_calender(since, until)

    def get_securities_list(self, market: int) -> list:
        pass

    def get_index_component(self, index_code: int) -> pd.DataFrame:
        pass

    # ----------------------------- Get Specify -----------------------------

    def get_securities_info(self, codes: str or list) -> [pd.DataFrame]:
        if isinstance(codes, str):
            codes = [codes]
        pass
        return []

    def get_securities_former_name(self, codes: str or list) -> [[]]:
        if isinstance(codes, str):
            codes = [codes]
        pass
        return []

    # ------------------------------- Update -------------------------------

    def check_update(self):
        pass

    # ------------------------------------------------- Trade Calender -------------------------------------------------

    def __check_update_trade_calender(self):
        update_table = DataTable().get_update_table()
        for exchange in MarketData.TRADE_EXCHANGE:
            latest_update = update_table.get_latest_update_time('TradeCalender', exchange, '')
            if latest_update is None:
                since = datetime(1990, 1, 1)
                until = today()
            elif latest_update != yesterday():
                since = latest_update
                until = today()
            if self.__do_update_trade_calender(exchange, since, until):
                    update_table.renew_update_time()

    def __do_update_trade_calender(self, exchange: str, since: datetime, until: datetime):
        plugins = self.__plugin.find_module_has_capacity('TradeCalender')
        for plugin in plugins:
            df = self.__plugin.execute_module_function(plugin, 'fetch_data', {
                'content': 'TradeCalender',
                'exchange': exchange,
                'since': since,
                'until': until,
            })
            if df is None or len(df) == 0:
                continue
            continuity, min_date, max_date = check_date_continuity(df, 'TradeDate')
            if not continuity:
                continue
            if min_date < since:
                df = df.loc[df['TradeDate'] >= since]
            ret = Database.get_utility_db().DataFrameToDB('TradeCalender', df, if_exists='append')
            return ret


    def __do_check_trade_calender_data(self, df: pd.DataFrame):
        pass

# ----------------------------------------------------- Test Code ------------------------------------------------------


def __build_instance() -> MarketData:
    from os import sys, path
    root_path = path.dirname(path.dirname(path.abspath(__file__)))
    plugin_path = root_path + '/Collector/'

    from Utiltity.plugin_manager import PluginManager
    collector_plugin = PluginManager(plugin_path)
    collector_plugin.refresh()
    return MarketData(collector_plugin)


def test_basic_feature():
    md = __build_instance()
    md.check_update_trade_calender()


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










