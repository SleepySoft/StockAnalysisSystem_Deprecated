# !usr/bin/env python
# -*- coding:utf-8 -*-

import traceback
import numpy as np
import pandas as pd
import tushare as ts
from Database.Database import Database


class StockCalendar:
    def __init__(self):
        self.__calendar = pd.DataFrame({'Date': [], 'IsOpen': []})

    def inited(self) -> bool:
        pass

    # Fetch data from internet.
    def fetch_data(self, **kw) -> bool:
        df = ts.trade_cal()
        if df is None:
            return False
        df.rename(columns={'calendarDate': 'Date', 'isOpen': 'IsOpen'}, inplace=True)
        df.index.name = 'Serial'
        self.__calendar = df
        return True

    # Auto check and update data to DB. Depends on collector's implementation.
    def check_update(self, **kw) -> bool:
        return self.force_update()

    # Force update all data in DB.
    def force_update(self, **kw) -> bool:
        return self.fetch_data() and self.dump_to_db()

    # Flush memory data to DB
    def dump_to_db(self, **kw) -> bool:
        if self.__calendar is None:
            return False
        return Database().GetUtilityDB().DataFrameToDB('StockCalendar', self.__calendar.reset_index())

    def load_from_db(self, **kw) -> bool:
        self.__calendar = Database().GetUtilityDB().DataFrameFromDB('StockCalendar', ["Date", "IsOpen"])
        if self.__calendar is not None:
            return True
        else:
            self.__calendar = pd.DataFrame({'Date': [], 'IsOpen': []})
            return False

    def dump_to_file(self, path: str, **kw) -> bool:
        if self.__calendar is None:
            return False
        # TODO:
        # ret = self.__calendar.to_csv(path)
        # return ret
        pass

    def load_from_file(self, path: str, **kw) -> bool:
        # TODO:
        pass



