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
        'plugin_name': 'dummy_plugin_for_test',
        'plugin_version': '0.0.0.1',
        'tags': ['test', 'dummy', 'analyzer']
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


def score(securities: [str], data_hub: DataHubEntry) -> [AnalysisResult]:
    pass


def inclusive(securities: [str], data_hub: DataHubEntry) -> ([str], [AnalysisResult]):
    pass


def exclusive(securities: [str], data_hub: DataHubEntry) -> ([str], [AnalysisResult]):
    pass



