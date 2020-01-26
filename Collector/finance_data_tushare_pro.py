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


# -------------------------------------------------------- Prob --------------------------------------------------------

CAPACITY_LIST = [
    'Finance.Audit',
    'Finance.BalanceSheet',
    'Finance.IncomeStatement',
    'Finance.CashFlowStatement',
]


def plugin_prob() -> dict:
    return {
        'plugin_name': 'finance_data_tushare_pro',
        'plugin_version': '0.0.0.1',
        'tags': ['tusharepro']
    }


def plugin_adapt(uri: str) -> bool:
    return uri in CAPACITY_LIST


def plugin_capacities() -> list:
    return CAPACITY_LIST


# ----------------------------------------------------------------------------------------------------------------------

def __fetch_finance_data(**kwargs) -> pd.DataFrame:
    result = check_execute_test_flag(**kwargs)
    if result is None:
        uri = kwargs.get('uri')
        period = kwargs.get('period')

        ts_code = pickup_ts_code(kwargs)
        since, until = normalize_time_serial(period, text2date('1900-01-01'), today())

        ts_since = since.strftime('%Y%m%d')
        ts_until = until.strftime('%Y%m%d')

        pro = ts.pro_api()
        # If we specify the exchange parameter, it raises error.

        if uri == 'Finance.Audit':
            result = pro.fina_audit(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
        elif uri == 'Finance.BalanceSheet':
            result = pro.balancesheet(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
        elif uri == 'Finance.IncomeStatement':
            result = pro.income(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
        elif uri == 'Finance.CashFlowStatement':
            result = pro.cashflow(ts_code=ts_code, start_date=ts_since, end_date=ts_until)
        else:
            result = None
    check_execute_dump_flag(result, **kwargs)

    if result is not None:
        result.rename(columns={'ts_code': 'stock_identity', 'end_date': 'period'}, inplace=True)
        result['stock_identity'] = result['stock_identity'].str.replace('.SH', '.SSE')
        result['stock_identity'] = result['stock_identity'].str.replace('.SZ', '.SZSE')
        result['period'] = pd.to_datetime(result['period'])

        if uri == 'Finance.Audit':
            result.rename(columns={'audit_result': 'conclusion',
                                   'audit_agency': 'agency',
                                   'audit_sign': 'sign'}, inplace=True)

    return result


# ----------------------------------------------------------------------------------------------------------------------

def query(**kwargs) -> pd.DataFrame or None:
    uri = kwargs.get('uri')
    if uri in CAPACITY_LIST:
        return __fetch_finance_data(**kwargs)
    else:
        return None


def validate(**kwargs) -> bool:
    nop(kwargs)
    return True
