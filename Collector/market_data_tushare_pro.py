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

CAPACITY_LIST = {
    'Marker.TradeCalender',
    'Marker.SecuritiesInfo',
    'Marker.IndexComponent',
}


def plugin_prob() -> dict:
    return {
        'plugin_name': 'market_data_tushare_pro',
        'plugin_version': '0.0.0.1',
        'tags': ['tusharepro']
    }


def plugin_adapt(uri: str) -> bool:
    return uri in CAPACITY_LIST


def plugin_capacities() -> list:
    return CAPACITY_LIST


# ----------------------------------------------------------------------------------------------------------------------

def __fetch_trade_calender(**kwargs) -> pd.DataFrame or None:
    exchange = kwargs.get('exchange', '')
    if str_available(exchange) and exchange not in ['SSE', 'SZSE']:
        return None

    time_serial = kwargs.get('datetime', None)
    since, until = normalize_time_serial(time_serial, text2date('1900-01-01'), today())

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


def __fetch_securities_info(**kwargs) -> pd.DataFrame or None:
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

def query(**kwargs) -> pd.DataFrame or None:
    uri = kwargs.get('uri')
    if uri == 'Marker.TradeCalender':
        return __fetch_trade_calender(**kwargs)
    elif uri == 'Marker.SecuritiesInfo':
        return __fetch_securities_info(**kwargs)
    elif uri == 'Marker.IndexComponent':
        return None
    else:
        return None


def validate(**kwargs) -> bool:
    nop(kwargs)
    return True



