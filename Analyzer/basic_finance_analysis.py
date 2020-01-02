import pandas as pd
from datetime import date

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import config
    from Utiltity.common import *
    from Utiltity.time_utility import *
    from Analyzer.AnalyzerUtility import *
    from DataHub.DataHubEntry import DataHubEntry
except Exception as e:
    sys.path.append(root_path)

    import config
    from Utiltity.common import *
    from Utiltity.time_utility import *
    from Analyzer.AnalyzerUtility import *
    from DataHub.DataHubEntry import DataHubEntry
finally:
    pass


# ----------------------------------------------------------------------------------------------------------------------

def plugin_prob() -> dict:
    return {
        'plugin_id': '7b59e0e4-5572-4cd8-8982-baa94f8af3d9',
        'plugin_name': 'basic_finance_analysis',
        'plugin_version': '0.0.0.1',
        'tags': ['finance', 'analyzer'],
        'methods': {
            'exclusive': [
                ('7a2c2ce7-9060-4c1c-bca7-71ca12e92b09', '黑名单',      '排除黑名单中的股票'),
                ('e639a8f1-f2f5-4d48-a348-ad12508b0dbb', '不足三年',    '排除上市不足三年的公司'),
                ('b0e34011-c5bf-4ac3-b6a4-c15e5ea150a6', '连续亏损',    '排除连续亏损的公司'),
                ('f39f14d6-b417-4a6e-bd2c-74824a154fc0', '地域限制',    '排除特定地域的公司'),
                ('1fdee036-c7c1-4876-912a-8ce1d7dd978b', '农林牧渔',    '排除农林牧渔相关行业'),
                ('e6ab71a9-0c9f-4500-b2db-d682af567f70', '商誉过高',    '排除商誉过高的公司'),
                ('d811ebd6-ee28-4d2f-b7e0-79ce0ecde7f7', '', ''),
                ('2c05bb4c-935e-4be7-9c04-ae12720cd757', '', ''),
                ('4ccedeea-b731-4b97-9681-d804838e351b', '', ''),
                ('f6fe627b-acbe-4b3f-a1fb-5edcd00d27b0', '', ''),
            ],
        }
    }


def plugin_adapt(method: str) -> bool:
    return method in methods_from_prob(plugin_prob())


def plugin_capacities() -> list:
    return [
        'exclusive',
    ]


# ----------------------------------------------------------------------------------------------------------------------

def analysis(securities: [str], methods: [str], data_hub: DataHubEntry) -> [AnalysisResult]:
    nop(data_hub)
    result = []
    for s in securities:
        end_char = s.split('.')[0][-1:]
        if '5d19927a-2ab1-11ea-aee4-eb8a702e7495' in methods:
            score = int(end_char)
            result.append(AnalysisResult('5d19927a-2ab1-11ea-aee4-eb8a702e7495', 'score',
                                         s, score, '传入的代码末位是几，就打几分'))
        if 'bc74b6fa-2ab1-11ea-8b94-03e35eea3ca4' in methods:
            score = 10 - int(end_char)
            result.append(AnalysisResult('bc74b6fa-2ab1-11ea-8b94-03e35eea3ca4', 'score',
                                         s, score, '传入的代码末位是几，就打10-几分'))
        if '6b23435c-2ab1-11ea-99a8-3f957097f4c9' in methods:
            passed = end_char in ['1', '2', '3', '4', '5']
            result.append(AnalysisResult('6b23435c-2ab1-11ea-99a8-3f957097f4c9', 'inclusive',
                                         s, passed, '只有代码末位是1-5的能通过此测试'))
        if 'd0b619ba-2ab1-11ea-ac32-43e650aafd4f' in methods:
            passed = end_char in ['5', '6', '7', '8', '9']
            result.append(AnalysisResult('d0b619ba-2ab1-11ea-ac32-43e650aafd4f', 'inclusive',
                                         s, passed, '只有代码末位是5-9的能通过此测试'))
        if '78ffae34-2ab1-11ea-88ff-634c407b44d3' in methods:
            blocked = s[0] in ['1', '2', '3', '4', '5']
            result.append(AnalysisResult('78ffae34-2ab1-11ea-88ff-634c407b44d3', 'exclusive',
                                         s, blocked, '只有代码第一位是1-5的会被排除'))
        if 'd905cdea-2ab1-11ea-9e79-ff65d4808d88' in methods:
            blocked = s[0] in ['5', '6', '7', '8', '9']
            result.append(AnalysisResult('d905cdea-2ab1-11ea-9e79-ff65d4808d88', 'exclusive',
                                         s, blocked, '只有代码第一位是5-9的会被排除'))
    return result






















