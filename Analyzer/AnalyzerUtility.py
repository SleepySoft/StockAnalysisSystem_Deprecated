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


class AnalysisResult:

    RESULT_TYPE = int
    RESULT_NONE = 0
    RESULT_TRUE = 1
    RESULT_FALSE = 2
    RESULT_SCORE = 3
    RESULT_UNSUPPORTED = 4

    def __init__(self, securities: str = '', result: RESULT_TYPE = RESULT_NONE):
        self.__score = 0
        self.__reason = ''
        self.__result = result
        self.__securities = securities

    # ---------------------------------------------

    def set_score(self, score: int):
        self.__score = score

    def set_reason(self, reason: str):
        self.__reason = reason

    def set_result(self, result: RESULT_TYPE):
        self.__result = result

    def set_securities(self, securities: str):
        self.__securities = securities

    # ---------------------------------------------

    def get_score(self) -> int:
        return self.__score

    def get_reason(self) -> str:
        return self.__reason

    def get_result(self) -> RESULT_TYPE:
        return self.__result

    def get_securities(self) -> str:
        return self.__securities

    # ------------------------------------------------------------------------------------------------------------------




















