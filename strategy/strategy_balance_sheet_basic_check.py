#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/09/01
@file: strategy_balance_sheet_basic_check.py
@function:
@modify:
"""


import strategy_manager as sm

class BalanceSheetBasicCheck:

    def __init__(self):
        self.__sas = None

    def Name(self) -> str:
        return 'BalanceSheetBasicCheck'
    def Depends(self) -> [str]:
        return []
    def SetEnvoriment(self, sAs):
        self.__sas = sAs

    def Instructions(self) -> str:
        return ''

    def Analysis(self, strategy_report: sm.StrategyReport) -> bool:
        self.__check_1('002184')
        return True

    # 检查货币资金
    def __check_1(self, stock_code: str):
        dc = self.__sas.GetDataCenter()
        df = dc.GetStockAnnualReportDataTable(stock_code, [
            '货币资金', '库存现金', '银行存款', '其他货币资金', '流动负债合计'], [])
        print(df)

    # 检查应收
    def __check_2(self, stock_code: str):
        dc = self.__sas.GetDataCenter()
        dc.GetStockAnnualReportDataTable(stock_code, ['应收账款'], ['应收票据'])


def GetModuleClass() -> object:
    return BalanceSheetBasicCheck
