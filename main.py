#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/08/21
@file: main.py
@function:
@modify:
"""
import traceback
import stock_analysis_system as sAs


def main():
    # cf = Collector_FinanceData_163()
    # cf.Fetch('002184')
    sAs.GetInstance.Init()
    # l = sAs.GetInstance.GetDataCenter().GetStockList()
    # dc = DataCollector()
    #
    # ctx = FetchContext()
    #
    # si = dc.FetchStockInformation(ctx, '')
    # ar = dc.FetchStockAnnualReport(ctx, '600000')

    # text = public.common.DownloadText('http://quotes.money.163.com/service/zcfzb_600000.html?type=year', 'gb2312')
    # text = public.common.DownloadText('http://quotes.money.163.com/service/lrb_600000.html?type=year', 'gb2312')
    # text = public.common.DownloadText('http://quotes.money.163.com/service/xjllb_600000.html?type=year', 'gb2312')
    # bytes = public.common.Download('http://quotes.money.163.com/service/xjllb_600000.html?type=year')
    # with open('d:/t.csv', 'wb') as f:
    #     f.write(bytes)
    # # df = pd.read_csv('d:/t.csv', encoding='utf-8')
    # df = pd.read_csv(BytesIO(bytes), encoding='gb2312')
    # print(df)

    # df = sAs.GetInstance.GetDataCenter().GetStockAnnualReportData(
    #     '600000', 2000, 2017, DataCenter.ANNUAL_REP_TYPE_ALL)
    # print(df)

    strategy_report = sAs.GetInstance.GetStrategyManager().ExecuteStrategy()


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
