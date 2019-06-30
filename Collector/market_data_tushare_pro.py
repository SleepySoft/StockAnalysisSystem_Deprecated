import pandas as pd
import tushare as ts
from datetime import date

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import config
    from Utiltity.common import *
    from Utiltity.time_utility import *
except Exception as e:
    sys.path.append(root_path)

    import config
    from Utiltity.common import *
    from Utiltity.time_utility import *
finally:
    pass

ts.set_token(config.TS_TOKEN)


# ----------------------------------------------------------------------------------------------------------------------

def plugin_prob() -> dict:
    return {
        'plugin_name': 'market_data_tushare_pro',
        'plugin_version': '0.0.0.1',
        'tags': ['tusharepro']
    }


def plugin_capacities() -> list:
    return [
        'TradeCalender',
        'SecuritiesInfo',
        'IndexComponent',
    ]


# ----------------------------------------------------------------------------------------------------------------------

def __fetch_trade_calender(**kwargs) -> pd.DataFrame:
    exchange = kwargs.get('exchange')
    since = kwargs.get('since')
    until = kwargs.get('until')
    if not isinstance(exchange, str) or \
       not isinstance(since, (date, str)) or \
       not isinstance(until, (date, str)):
        return None
    if isinstance(since, str):
        since = text2date(since)
    if isinstance(until, str):
        since = text2date(until)
    ts_since = since.strftime('%Y%m%d')
    ts_until = until.strftime('%Y%m%d')

    pro = ts.pro_api()
    # If we specify the exchange parameter, it raises error.
    result = pro.trade_cal('', start_date=ts_since, end_date=ts_until)

    if result is not None:
        result.rename(columns={'exchange': 'exchange', 'cal_date': 'trade_date', 'is_open': 'status'}, inplace=True)
        # Because tushare only support SSE and they are the same
        if exchange == 'SZSE':
            result.drop(result[result.exchange != 'SSE'].index, inplace=True)
            result['exchange'] = 'SZSE'
        else:
            result.drop(result[result.exchange != exchange].index, inplace=True)
        result['trade_date'] = pd.to_datetime(result['trade_date'])
    return result


def __fetch_securities_info(**kwargs) -> pd.DataFrame:
    # exchange = kwargs.get('exchange')
    # if isinstance(exchange, str):
    #     exchange = [str]

    pro = ts.pro_api()
    # If we specify the exchange parameter, it raises error.
    result = pro.stock_basic()

    if result is not None:
        result.rename(columns={'symbol': 'code',
                               'curr_type': 'currency',
                               'list_date': 'listing_date',
                               'delist_date': 'delisting_date',
                               'stock_connect': 'stock_connect'}, inplace=True)
        if 'code' not in result.columns:
            return None
        if 'listing_date' in result.columns:
            result['listing_date'] = pd.to_datetime(result['listing_date'], format='%Y-%m-%d')
        if 'delisting_date' in result.columns:
            result['delisting_date'] = pd.to_datetime(result['delisting_date'], format='%Y-%m-%d')
        if 'exchange' not in result.columns:
            result['exchange'] = result['ts_code'].apply(lambda val: val.split('.')[1])
            result['exchange'] = result['exchange'].apply(lambda val: 'SSE' if val == 'SH' else val)
            result['exchange'] = result['exchange'].apply(lambda val: 'SZSE' if val == 'SZ' else val)
    return result


# ----------------------------------------------------------------------------------------------------------------------

def validate(**kwargs) -> bool:
    content = kwargs.get('content')
    return True


def fetch_data(**kwargs) -> pd.DataFrame:
    content = kwargs.get('content')
    if content == 'TradeCalender':
        return __fetch_trade_calender(**kwargs)
    elif content == 'SecuritiesInfo':
        return __fetch_securities_info(**kwargs)
    else:
        return None

