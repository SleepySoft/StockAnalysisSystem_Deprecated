import datetime
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


def param_as_date_str(kwargs: dict, param: str) -> str:
    dt = kwargs.get(param)
    if dt is None:
        return ''
    if not isinstance(dt, (datetime.datetime, datetime.date, str)):
        return ''
    if isinstance(dt, str):
        dt = text2date(dt)
    return dt.strftime('%Y%m%d')


def code_exchange_to_ts_code(code: str, exchange: str) -> str:
    if exchange not in ['SSE', 'SZSE']:
        return ''
    return code + '.' + ('SH' if exchange == 'SSE' else 'SZ')


def pickup_since_until_as_date(kwargs: dict) -> (str, str):
    since = kwargs.get('since', None)
    until = kwargs.get('until', None)
    return param_as_date_str(kwargs, since), param_as_date_str(kwargs, until)


def stock_identity_to_ts_code(stock_identity: str) -> str:
    if stock_identity.endswith('.SSE'):
        return stock_identity.replace('.SSE', '.SH')
    if stock_identity.endswith('.SZSE'):
        return stock_identity.replace('.SZSE', '.SZ')
    return ''


def pickup_ts_code(kwargs: dict) -> str:
    stock_identity = kwargs.get('stock_identity')
    if stock_identity is not None:
        return stock_identity_to_ts_code(stock_identity)
    code = kwargs.get('code')
    exchange = kwargs.get('exchange')
    if code is None or exchange is None:
        return ''
    if not isinstance(code, str) or not isinstance(exchange, str):
        return ''
    return code_exchange_to_ts_code(code, exchange)










