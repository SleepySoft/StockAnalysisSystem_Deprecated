import pandas as pd
from datetime import datetime


class MarketData:
    SECURITIES_SH = 0x01
    SECURITIES_SZ = 0x02
    SECURITIES_A_SHARES = SECURITIES_SH & SECURITIES_SZ

    def __init__(self):
        pass

    # ----------------------------- Gets List -----------------------------

    def get_trade_calender(self, since: datetime = None, until: datetime = None) -> dict:
        pass

    def get_securities_list(self, market: int) -> list:
        pass

    def get_index_component(self, index_code: int) -> pd.DataFrame:
        pass

    # ----------------------------- Get Specify -----------------------------

    def get_securities_info(self, codes: str or list) -> [pd.DataFrame]:
        if isinstance(codes, str):
            codes = [codes]
        pass
        return []

    def get_securities_former_name(self, codes: str or list) -> [[]]:
        if isinstance(codes, str):
            codes = [codes]
        pass
        return []

    # ------------------------------- Update -------------------------------

    def check_update(self):
        pass









