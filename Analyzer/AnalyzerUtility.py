import datetime
import pandas as pd
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


def methods_from_prob(prob: dict) -> []:
    return methods_from_method_list(prob.get('methods', []))


def methods_from_method_list(method_list: list) -> []:
    return [method for method, _, _, _ in method_list]


def standard_dispatch_analysis(securities: [str], methods: [str], data_hub, database,
                               method_list: list) -> []:
    result_list = []
    for query_method in methods:
        for hash_id, _, _, function_entry in method_list:
            if hash_id == query_method:
                if function_entry is None:
                    print('Method ' + hash_id + ' not implemented yet.')
                else:
                    result = function_entry(securities, data_hub, database)
                    if result is not None or len(result) > 0:
                        result_list.append((query_method, result))
                break
    return result_list


# ----------------------------------------------------------------------------------------------------------------------

class AnalysisResult:

    SCORE_MIN = 0
    SCORE_MAX = 100
    SCORE_PASS = SCORE_MAX
    SCORE_FAIL = SCORE_MIN
    SCORE_NOT_APPLIED = None

    def __init__(self, securities: str, score: int or bool, reason: str or [str] = ''):
        self.method = ''
        self.securities = securities

        if isinstance(score, bool):
            self.score = AnalysisResult.SCORE_PASS if score else AnalysisResult.SCORE_FAIL
        elif isinstance(score, (int, float)):
            self.score = score
            self.score = min(self.score, AnalysisResult.SCORE_MAX)
            self.score = max(self.score, AnalysisResult.SCORE_MIN)
        else:
            self.score = score

        if reason is None:
            self.reason = ''
        elif isinstance(reason, (list, tuple)):
            self.reason = '\n'.join(reason)
        else:
            self.reason = reason


# ------------------------------------------------------------------------------------------------------------------


"""
The results should look like:

method1           method2           method3           ...           methodM
m1_result1        m2_result1        m3_result1                      mM_result1
m1_result2        m2_result2        m3_result2                      mM_result2
m1_result3        m2_result3        m3_result3                      mM_result3
.                 .                 .                               .
.                 .                 .                               .
.                 .                 .                               .
m1_resultN        m2_resultN        m3_resultN                      mM_resultN
"""


def get_securities_in_result(result: dict) -> [str]:
    securities = []
    for method, results in result.items():
        for r in results:
            if str_available(r.securities) and r.securities not in securities:
                securities.append(r.securities)
    return securities


def pick_up_pass_securities(result: dict, score_threshold: int) -> [str]:
    securities = get_securities_in_result(result)
    for method, results in result.items():
        for r in results:
            if r.score < score_threshold and r.securities in securities:
                securities.remove(r.securities)
    return securities

















