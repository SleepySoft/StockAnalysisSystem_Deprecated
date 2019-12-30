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

    RESULT_NONE = None
    RESULT_TRUE = True
    RESULT_FALSE = False
    RESULT_SCORE = int

    def __init__(self, method: str, method_type: str, securities: str, result: any, reason: str = ''):
        self.method = method
        self.method_type = method_type
        self.securities = securities
        self.result = result
        self.reason = reason

    # ------------------------------------------------------------------------------------------------------------------




















