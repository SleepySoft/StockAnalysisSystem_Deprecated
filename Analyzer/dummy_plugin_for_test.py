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
        'plugin_id': '2806f676-2aad-11ea-8c57-87a2a5d9cf76',
        'plugin_name': 'dummy_plugin_for_test',
        'plugin_version': '0.0.0.1',
        'tags': ['test', 'dummy', 'analyzer'],
        'manual': {
            'score': [
                ('5d19927a-2ab1-11ea-aee4-eb8a702e7495', '评分测试1', '传入的代码末位是几，就打几分。'),
                ('bc74b6fa-2ab1-11ea-8b94-03e35eea3ca4', '评分测试2', '传入的代码末位是几，就打10-几分。'),
            ],
            'inclusive': [
                ('6b23435c-2ab1-11ea-99a8-3f957097f4c9', '包含测试1', '只有代码末位是1-5的能通过此测试。'),
                ('d0b619ba-2ab1-11ea-ac32-43e650aafd4f', '包含测试2', '只有代码末位是5-9的能通过此测试。'),
            ],
            'exclusive': [
                ('78ffae34-2ab1-11ea-88ff-634c407b44d3', '排除测试1', '只有代码第一位是1-5的会被排除'),
                ('d905cdea-2ab1-11ea-9e79-ff65d4808d88', '排除测试2', '只有代码第一位是5-9的会被排除'),
            ],
        }
    }


def plugin_adapt(uri: str) -> bool:
    return uri.startswith('test.')


def plugin_capacities() -> list:
    return [
        'score',
        'inclusive',
        'exclusive',
    ]


# ----------------------------------------------------------------------------------------------------------------------

def manual() -> dict:
    return {
        'score': (),
        'inclusive': (),
        'exclusive': (),
    }


def score(securities: [str], methods: [str], data_hub: DataHubEntry) -> [AnalysisResult]:
    pass


def inclusive(securities: [str], methods: [str], data_hub: DataHubEntry) -> ([str], [AnalysisResult]):
    pass


def exclusive(securities: [str], methods: [str], data_hub: DataHubEntry) -> ([str], [AnalysisResult]):
    pass



