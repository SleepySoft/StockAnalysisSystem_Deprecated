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

def __fetch_finance_data(**kwargs) -> pd.DataFrame:
    code = kwargs.get('code')
    since = kwargs.get('since')
    until = kwargs.get('until')
    content = kwargs.get('content')
    exchange = kwargs.get('exchange')
    if not isinstance(code, str) or \
       not isinstance(exchange, str) or \
       not isinstance(since, (date, str)) or \
       not isinstance(until, (date, str)):
        return None
    if exchange not in ['SSE', 'SZSE']:
        return None
    if isinstance(since, str):
        since = text2date(since)
    if isinstance(until, str):
        since = text2date(until)
    ts_since = since.strftime('%Y%m%d')
    ts_until = until.strftime('%Y%m%d')
    ts_code = code + '.' + ('SH' if exchange == 'SSE' else 'SZ')

    pro = ts.pro_api()
    # If we specify the exchange parameter, it raises error.

    if content == 'BalanceSheet':
        result = pro.balancesheet(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
    elif content == 'CashFlowStatement':
        result = pro.cashflow(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
    elif content == 'income':
        result = pro.balancesheet(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
    else:
        result = None

    # if result is not None:
    #     result.rename(columns={'exchange': 'exchange', 'cal_date': 'trade_date', 'is_open': 'status'}, inplace=True)
    #     # Because tushare only support SSE and they are the same
    #     if exchange == 'SZSE':
    #         result.drop(result[result.exchange != 'SSE'].index, inplace=True)
    #         result['exchange'] = 'SZSE'
    #     else:
    #         result.drop(result[result.exchange != exchange].index, inplace=True)
    #     result['trade_date'] = pd.to_datetime(result['trade_date'])

    return result


# ----------------------------------------------------------------------------------------------------------------------

def validate(**kwargs) -> bool:
    content = kwargs.get('content')
    return True


def fetch_data(**kwargs) -> pd.DataFrame:
    content = kwargs.get('content')
    if content == 'BalanceSheet':
        return __fetch_finance_data(**kwargs)
    elif content == 'CashFlowStatement':
        return __fetch_finance_data(**kwargs)
    elif content == 'IncomeStatement':
        return __fetch_finance_data(**kwargs)
    else:
        return None

