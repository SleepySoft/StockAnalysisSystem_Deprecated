import pandas as pd
from datetime import date

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import config
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Analyzer.AnalyzerUtility import *
    from DataHub.DataHubEntry import DataHubEntry
    from Database.DatabaseEntry import DatabaseEntry
except Exception as e:
    sys.path.append(root_path)

    import config
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Analyzer.AnalyzerUtility import *
    from DataHub.DataHubEntry import DataHubEntry
    from Database.DatabaseEntry import DatabaseEntry
finally:
    pass


# ----------------------------------------------------------------------------------------------------------------------

def analysis_black_list(securities: str, data_hub: DataHubEntry, database: DatabaseEntry) -> [AnalysisResult]:
    nop(data_hub)
    result = []
    black_list = database.get_black_table().get_name_list()
    for s in securities:
        exclude = s in black_list
        reason = 'In black list' if exclude else 'Not in black list'
        result.append(AnalysisResult('7a2c2ce7-9060-4c1c-bca7-71ca12e92b09', s, not exclude, reason))
    return result


def analysis_less_than_3_years(securities: str, data_hub: DataHubEntry, database: DatabaseEntry) -> [AnalysisResult]:
    nop(database)
    result = []
    df = data_hub.get_data_center().query('Market.SecuritiesInfo', securities)
    for s in securities:
        df_slice = df[df['stock_identity'] == s]
        listing_date = get_dataframe_slice_item(df_slice, 'listing_date', 0, now())
        exclude = now().year - listing_date.year < 3
        reason = 'Less than 3 years' if exclude else 'More than 3 years'
        result.append(AnalysisResult('e639a8f1-f2f5-4d48-a348-ad12508b0dbb', s, not exclude, reason))
    return result


def analysis_location_limitation(securities: str, data_hub: DataHubEntry, database: DatabaseEntry) -> [AnalysisResult]:
    nop(database)
    result = []
    df = data_hub.get_data_center().query('Market.SecuritiesInfo', securities)
    for s in securities:
        df_slice = df[df['stock_identity'] == s]
        area = get_dataframe_slice_item(df_slice, 'area', 0, '')
        exclude = area in ['黑龙江', '辽宁', '吉林']
        reason = 'Less than 3 years' if exclude else 'More than 3 years'
        result.append(AnalysisResult('f39f14d6-b417-4a6e-bd2c-74824a154fc0', s, not exclude, reason))
    return result


def analysis_finance_report_sign(securities: str, data_hub: DataHubEntry, database: DatabaseEntry) -> [AnalysisResult]:
    nop(database)
    result = []
    df = data_hub.get_data_center().query('Finance.Audit', securities)
    for s in securities:
        if 'stock_identity' in df.columns:
            df_slice = df[df['stock_identity'] == s]

            conclusion = get_dataframe_slice_item(df_slice, 'conclusion', 0, '')
            agency = get_dataframe_slice_item(df_slice, 'agency', 0, '')
            sign = get_dataframe_slice_item(df_slice, 'sign', 0, '')

            exclude = conclusion != ''
        else:
            exclude = False

        reason = 'Less than 3 years' if exclude else 'More than 3 years'
        result.append(AnalysisResult('f39f14d6-b417-4a6e-bd2c-74824a154fc0', s, not exclude, reason))
    return result


def analysis_consecutive_losses(securities: str, data_hub: DataHubEntry, database: DatabaseEntry) -> [AnalysisResult]:
    pass


# ----------------------------------------------------------------------------------------------------------------------

METHOD_LIST = [
    ('7a2c2ce7-9060-4c1c-bca7-71ca12e92b09', '黑名单',      '排除黑名单中的股票',        analysis_black_list),
    ('e639a8f1-f2f5-4d48-a348-ad12508b0dbb', '不足三年',    '排除上市不足三年的公司',    analysis_less_than_3_years),
    ('f39f14d6-b417-4a6e-bd2c-74824a154fc0', '地域限制',    '排除特定地域的公司',        analysis_location_limitation),
    ('3b01999c-3837-11ea-b851-27d2aa2d4e7d', '财报非标',    '排除财报非标的公司',        analysis_finance_report_sign),

    ('1fdee036-c7c1-4876-912a-8ce1d7dd978b', '农林牧渔',    '排除农林牧渔相关行业',     None),
    ('b0e34011-c5bf-4ac3-b6a4-c15e5ea150a6', '连续亏损',    '排除连续亏损的公司',       None),
    ('e6ab71a9-0c9f-4500-b2db-d682af567f70', '商誉过高',    '排除商誉过高的公司',       None),
    # ('d811ebd6-ee28-4d2f-b7e0-79ce0ecde7f7', '', ''),
    # ('2c05bb4c-935e-4be7-9c04-ae12720cd757', '', ''),
    # ('4ccedeea-b731-4b97-9681-d804838e351b', '', ''),
    # ('f6fe627b-acbe-4b3f-a1fb-5edcd00d27b0', '', ''),
]


def plugin_prob() -> dict:
    return {
        'plugin_id': '7b59e0e4-5572-4cd8-8982-baa94f8af3d9',
        'plugin_name': 'basic_finance_analysis',
        'plugin_version': '0.0.0.1',
        'tags': ['finance', 'analyzer'],
        'methods': METHOD_LIST,
    }


def plugin_adapt(method: str) -> bool:
    return method in methods_from_prob(plugin_prob())


def plugin_capacities() -> list:
    return [
        'exclusive',
    ]


# ----------------------------------------------------------------------------------------------------------------------

def analysis(securities: [str], methods: [str], data_hub: DataHubEntry, database: DatabaseEntry) -> [AnalysisResult]:
    return standard_dispatch_analysis(securities, methods, data_hub, database, METHOD_LIST)



















