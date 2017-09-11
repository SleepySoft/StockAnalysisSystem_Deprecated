#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/08/15
@file: stock_fina_163.py
@function:
@modify:
"""
import traceback
import numpy as np
import pandas as pd
import public.common
from io import BytesIO


class StockFinancialDataFrom163:

    def Name(self) -> str:
        return 'StockFinancialDataFrom163'
    def Depends(self) -> [str]:
        return []
    def SetEnvoriment(self, sAs):
        pass

    # Key: balance_sheet, income_statement, cash_flow_statement
    # Columns: ......
    def FetchStockAnnualReport(self, stock_code: str, report_type: list, extra_param=None) -> {str: pd.DataFrame}:
        result = {}
        if 'balance_sheet' in report_type:
            url_balance_sheets = 'http://quotes.money.163.com/service/zcfzb_' + stock_code + '.html?type=year'
            df_balance_sheets = self.__fetch_from_163(url_balance_sheets)
            result['balance_sheet'] = df_balance_sheets
        if 'income_statement' in report_type:
            url_income_statement = 'http://quotes.money.163.com/service/lrb_' + stock_code + '.html?type=year'
            df_income_statement = self.__fetch_from_163(url_income_statement)
            result['income_statement'] = df_income_statement
        if 'cash_flow_statement' in report_type:
            url_cash_flow_statement = 'http://quotes.money.163.com/service/xjllb_' + stock_code + '.html?type=year'
            df_cash_flow_statement = self.__fetch_from_163(url_cash_flow_statement)
            result['cash_flow_statement'] = df_cash_flow_statement
        return result

        # name_list = []
        # name_list.extend(df_balance_sheets.index)
        # name_list.extend(df_income_statement.index)
        # name_list.extend(df_cash_flow_statement.index)
        #
        # named_list = []
        # unnamed_list = []
        # for n in name_list:
        #     s = sAs.GetInstance.GetAliasesTable().GetStandardName(n.replace('(万元)', ''))
        #     if s == '':
        #         unnamed_list.append(n)
        #     else:
        #         named_list.append(n)
        # print(unnamed_list)

        # with open('Index.txt', 'w') as f:
        #     for l in df_balance_sheets.index:
        #         f.write(l + '\r\n')

    def __fetch_from_163(self, url: str) -> pd.DataFrame:
        try:
            df = public.common.DownloadCsvAsDF(url, 'gb2312')
            df = df.T
            df.columns = df.iloc[0]
            df = df[1:]
            df.columns = df.columns.str.strip()
            df['报告日期'].replace('', np.nan, inplace=True)
            df.dropna(subset=['报告日期'], inplace=True)
            df.set_index('报告日期', inplace=True, drop=False)
            return df
        except Exception as e:
            print('Error =>', e)
            print('Error =>', traceback.format_exc())
            return None
        finally:
            pass

def GetModuleClass() -> object:
    return StockFinancialDataFrom163
