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
    methods = []
    method_dict = prob.get('prob', {})
    for capacity, method_list in method_dict:
        for method in method_list:
            methods.append(method[0])
    return methods


class AnalysisResult:

    SCORE_MIN = 0
    SCORE_MAX = 100
    SCORE_PASS = SCORE_MAX
    SCORE_FAIL = SCORE_MIN

    def __init__(self, method: str, securities: str, score: int or bool, reason: str = ''):
        self.method = method
        self.securities = securities
        if isinstance(score, bool):
            self.score = AnalysisResult.SCORE_PASS if score else AnalysisResult.SCORE_FAIL
        elif isinstance(score, (int, float)):
            self.score = score
            self.score = min(self.score, AnalysisResult.SCORE_MAX)
            self.score = max(self.score, AnalysisResult.SCORE_MIN)
        self.reason = reason

    # ------------------------------------------------------------------------------------------------------------------




















