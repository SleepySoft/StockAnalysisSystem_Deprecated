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


# ------------------------------------------------------- Fields -------------------------------------------------------

FIELDS = {
    'Market.TradeCalender': {
        'exchange':                      '交易所',                            # SSE上交所;SZSE深交所
        'cal_date':                      '日历日期',
        'is_open':                       '是否交易',                           # 0休市;1交易
        'pretrade_date':                 '上一个交易日',
    },
    'Market.NamingHistory': {
        'ts_code':                       'TS代码',
        'name':                          '证券名称',
        'start_date':                    '开始日期',
        'end_date':                      '结束日期',
        'ann_date':                      '公告日期',
        'change_reason':                 '变更原因',
    },
    'Market.SecuritiesInfo': {
        'ts_code':                       'TS代码',
        'symbol':                        '股票代码',
        'name':                          '股票名称',
        'area':                          '所在地域',
        'industry':                      '所属行业',
        'fullname':                      '股票全称',
        'enname':                        '英文全称',
        'market':                        '市场类型',                           # 主板/中小板/创业板/科创板
        'exchange':                      '交易所代码',
        'curr_type':                     '交易货币',
        'list_status':                   '上市状态',                           # L上市;D退市;P暂停上市
        'list_date':                     '上市日期',
        'delist_date':                   '退市日期',
        'is_hs':                         '是否沪深港通标的',                       # N否;H沪股通;S深股通
    },
    'Market.IndexComponent': {
        'ts_code':                       'TS代码',
        'symbol':                        '股票代码',
        'name':                          '股票名称',
        'area':                          '所在地域',
        'industry':                      '所属行业',
        'fullname':                      '股票全称',
        'enname':                        '英文全称',
        'market':                        '市场类型',                           # 主板/中小板/创业板/科创板
        'exchange':                      '交易所代码',
        'curr_type':                     '交易货币',
        'list_status':                   '上市状态',                           # L上市;D退市;P暂停上市
        'list_date':                     '上市日期',
        'delist_date':                   '退市日期',
        'is_hs':                         '是否沪深港通标的',                       # N否;H沪股通;S深股通
    },
}


# -------------------------------------------------------- Prob --------------------------------------------------------

def plugin_prob() -> dict:
    return {
        'plugin_name': 'market_data_tushare_pro',
        'plugin_version': '0.0.0.1',
        'tags': ['tusharepro']
    }


def plugin_adapt(uri: str) -> bool:
    return uri in FIELDS.keys()


def plugin_capacities() -> list:
    return list(FIELDS.keys())


# ----------------------------------------------------------------------------------------------------------------------

def __fetch_trade_calender(**kwargs) -> pd.DataFrame or None:
    exchange = kwargs.get('exchange', '')
    if str_available(exchange) and exchange not in ['SSE', 'SZSE', 'A-SHARE']:
        return None

    result = check_execute_test_flag(**kwargs)
    if result is None:
        time_serial = kwargs.get('trade_date', None)
        since, until = normalize_time_serial(time_serial, default_since(), today())

        ts_since = since.strftime('%Y%m%d')
        ts_until = until.strftime('%Y%m%d')

        pro = ts.pro_api(config.TS_TOKEN)
        # If we specify the exchange parameter, it raises error.
        result = pro.trade_cal('', start_date=ts_since, end_date=ts_until)
    check_execute_dump_flag(result, **kwargs)

    if result is not None:
        result.rename(columns={'exchange': 'exchange', 'cal_date': 'trade_date', 'is_open': 'status'}, inplace=True)
        # Because tushare only support SSE and they are the same
        if exchange == 'SZSE' or exchange == 'A-SHARE':
            result.drop(result[result.exchange != 'SSE'].index, inplace=True)
            result['exchange'] = exchange
        else:
            result.drop(result[result.exchange != exchange].index, inplace=True)
        result['trade_date'] = pd.to_datetime(result['trade_date'])
    return result


def __fetch_naming_history(**kwargs):
    result = check_execute_test_flag(**kwargs)
    if result is None:
        ts_code = pickup_ts_code(kwargs)
        period = kwargs.get('naming_date')
        since, until = normalize_time_serial(period, default_since(), today())

        ts_since = since.strftime('%Y%m%d')
        ts_until = until.strftime('%Y%m%d')

        pro = ts.pro_api(config.TS_TOKEN)
        result = pro.namechange(ts_code=ts_code, start_date=ts_since, end_date=ts_until,
                                fields='ts_code,name,start_date,end_date,ann_date,change_reason')
    check_execute_dump_flag(result, **kwargs)

    if result is not None:
        if 'start_date' in result.columns:
            result['naming_date'] = pd.to_datetime(result['start_date'], format='%Y-%m-%d')
        if 'stock_identity' not in result.columns:
            result['stock_identity'] = result['ts_code'].apply(ts_code_to_stock_identity)

    return result


def __fetch_securities_info(**kwargs) -> pd.DataFrame or None:
    result = check_execute_test_flag(**kwargs)
    if result is None:
        pro = ts.pro_api(config.TS_TOKEN)
        # If we specify the exchange parameter, it raises error.
        result = pro.stock_basic(fields='ts_code,symbol,name,area,industry,fullname,list_date,'
                                        'enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
    check_execute_dump_flag(result, **kwargs)

    if result is not None:
        result['list_date'] = pd.to_datetime(result['list_date'], format='%Y-%m-%d')
        result['delist_date'] = pd.to_datetime(result['delist_date'], format='%Y-%m-%d')

        result['listing_date'] = pd.to_datetime(result['list_date'], format='%Y-%m-%d')

        if 'code' not in result.columns:
            result['code'] = result['ts_code'].apply(lambda val: val.split('.')[0])
        if 'exchange' not in result.columns:
            result['exchange'] = result['ts_code'].apply(lambda val: val.split('.')[1])
            result['exchange'] = result['exchange'].apply(lambda val: 'SSE' if val == 'SH' else val)
            result['exchange'] = result['exchange'].apply(lambda val: 'SZSE' if val == 'SZ' else val)
        result['stock_identity'] = result['code'] + '.' + result['exchange']

    return result


# ----------------------------------------------------------------------------------------------------------------------

def query(**kwargs) -> pd.DataFrame or None:
    uri = kwargs.get('uri')
    if uri == 'Market.TradeCalender':
        return __fetch_trade_calender(**kwargs)
    elif uri == 'Market.NamingHistory':
        return __fetch_naming_history(**kwargs)
    elif uri == 'Market.SecuritiesInfo':
        return __fetch_securities_info(**kwargs)
    elif uri == 'Market.IndexComponent':
        return None
    else:
        return None


def validate(**kwargs) -> bool:
    nop(kwargs)
    return True



