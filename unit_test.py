#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/09/07
@file: unit_test.py
@function:
@modify:
"""


import traceback
import pandas as pd

import public
import data_center as dc
import stock_analysis_system as sAs


def test_sub_dataframe():
    df = pd.DataFrame({
        'column1': range(100, 105),
        'column2': range(300, 305),
        'column3': range(500, 505)
    })
    df = df.set_index([[2001, 2002, 2003, 2005, 2006]])
    print(df)

    # df = dc.DataCenter.SubAnnualReportTable(df, [2001, 2003], ['column2', 'column3'])
    df = dc.DataCenter.SubAnnualReportTable(df, [2001, 2004, 2005], ['column1', 'column4'])
    print(df)


def test__DataCenterCore_GetStockAnnualReportData():
    dcc = dc.DataCenterCore()
    df = dcc.GetStockAnnualReportData(
        '600000', 2000, 2017, public.constant.ANNUAL_REPORT_TYPES)
    print(df)


def test__DataCenter_GetStockAnnualReportDataTable():
    df_map = sAs.GetInstance.GetDataCenter().GetStockAnnualReportDataTable(
        '600000',
        ['货币资金(万元)', '结算备付金(万元)', '拆出资金(万元)', 'Fake', '衍生金融资产(万元)'],
        list(range(2001, 2010))
    )
    print(df_map)


def test__AliasesTable_ExportTable():
    sAs.GetInstance.GetAliasesTable().ExportTable('D:/AliasesTable.csv')


def test_run_strategy():
    all_strategy = sAs.GetInstance.GetStrategyManager().GetStrategyNameList()
    sAs.GetInstance.GetStrategyManager().ExecuteStrategy(all_strategy)


def main():
    sAs.GetInstance.Init()
    # test_sub_dataframe()  # <- Passed on 20170908
    # test__DataCenterCore_GetStockAnnualReportData()  # <- Passed on 20170908
    # test__DataCenter_GetStockAnnualReportDataTable()  # <- Passed on 20170909
    # test__AliasesTable_ExportTable()  # <- Passed on 20170909
    test_run_strategy()

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass
