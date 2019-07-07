import pandas as pd
import tushare as ts
from datetime import date

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import config
    from Utiltity.common import *
    from Utiltity.time_utility import *
    from Collector.CollectorUtility import *
except Exception as e:
    sys.path.append(root_path)

    import config
    from Utiltity.common import *
    from Utiltity.time_utility import *
    from Collector.CollectorUtility import *
finally:
    pass

ts.set_token(config.TS_TOKEN)


# ----------------------------------------------------------------------------------------------------------------------

def plugin_prob() -> dict:
    return {
        'plugin_name': 'finance_data_tushare_pro',
        'plugin_version': '0.0.0.1',
        'tags': ['tusharepro']
    }


def plugin_capacities() -> list:
    return [
        'BalanceSheet',
        'CashFlowStatement',
        'IncomeStatement',
    ]


# ----------------------------------------------------------------------------------------------------------------------

def __fetch_finance_data(**kwargs) -> pd.DataFrame:
    content = kwargs.get('content')
    report_type = kwargs.get('report_type')
    if not isinstance(content, str) or \
       not isinstance(report_type, str):
        return None
    ts_code = pickup_ts_code(kwargs)
    ts_since, ts_until = pickup_since_until_as_date(kwargs)

    pro = ts.pro_api()
    # If we specify the exchange parameter, it raises error.

    if content == 'BalanceSheet':
        result = pro.balancesheet(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
    elif content == 'CashFlowStatement':
        result = pro.cashflow(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
    elif content == 'IncomeStatement':
        result = pro.balancesheet(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
    else:
        print('Unknown content: ' + content)
        result = None

    if result is not None:
        result.to_csv(root_path + '/TestData/trade_calender.csv')

    # if result is not None:
    #     result.rename(columns={'ts_code': 'identity', 'end_date': 'period'}, inplace=True)
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

