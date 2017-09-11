#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@version:
author:Sleepy
@time: 2017/08/09
@file: data_center.py
@function:
@modify:
"""


import numpy as np
import pandas as pd
import json

import data_collector
import public.common
import public.constant
import stock_analysis_system as sAs


# Query, Download and Storage
class DataCenterCore:
    STOCK_INFORMATION_TABLE_DESC = [
        ['company_name', 'varchar(255)'],
        ['stock_name_a', 'varchar(16)'],
        ['stock_code_a', 'varchar(16)'],
        ['stock_name_b', 'varchar(16)'],
        ['stock_code_b', 'varchar(16)'],
        ['industry', 'varchar(100)'],

        ['area', 'varchar(100)'],
        ['city', 'varchar(100)'],
        ['provinces', 'varchar(100)'],
        ['web_address', 'varchar(100)'],

        ['reg_address', 'varchar(255)'],
        ['english_name', 'varchar(255)'],
        ['listing_date_a', 'date'],
        ['listing_date_b', 'date']
        ]

    FINANCIAL_STATEMENTS_FIELDS = [
        'StockCode',
        'AccountingAnnual',
        'FinancialData'
    ]
    FINANCIAL_STATEMENTS_TABLE_DESC = [
        ['Serial', 'int'],
        ['StockCode', 'varchar(20)'],
        ['AccountingAnnual', 'int'],
        ['FinancialData', 'TEXT'],
    ]

    def __init__(self):
        pass

    def Init(self) -> bool:
        execute_statues = True
        for t in public.constant.ANNUAL_REPORT_TYPES:
            if not sAs.GetInstance.GetDataCenterDB().TableExists(t):
                execute_statues = execute_statues and sAs.GetInstance.GetDataCenterDB().CreateTable(
                    t, DataCenterCore.FINANCIAL_STATEMENTS_TABLE_DESC)
        if not execute_statues:
            print('DataCenterCore : Financial Statement Table Create Fail!')
            return False
        return True

    # [(stock_name : stock_code)]
    def GetStockList(self) -> [(str, str)]:
        result = self.__query_stock_list()
        if result is None or len(result) == 0:
            if not self.__download_stock_information():
                return None
        return self.__query_stock_list()

    # In:
    #   report_type -> public.constant.ANNUAL_REPORT_TYPES
    def GetStockAnnualReportData(self, stock_code: str, year_from: int, year_to: int, report_type: [str]) -> {str: pd.DataFrame}:
        condition = " StockCode = '" + stock_code + "'"
        if year_from > 0 and year_to > 0:
            year_from = 0 if year_from < 0 else year_from
            year_to = year_from if year_to < year_from else year_to
            condition += ' AND AccountingAnnual >= ' + str(year_from) + ' AND AccountingAnnual <= ' + str(year_to)
        result = {}
        for t in report_type:
            result[t] = self.__get_annual_report(stock_code, t, condition)
        return result

    # -------------------------------------- private --------------------------------------

    # --------------------------- Stock list ---------------------------

    def __query_stock_list(self) -> [(str, str)]:
        return sAs.GetInstance.GetDataCenterDB().ListFromDB(
            'StockInformation', ['stock_code_a', 'stock_name_a'])

    def __download_stock_information(self) -> bool:
        ctx = data_collector.FetchContext()
        ctx.SpecifyPlugin('MarketInformationFromSZSE')
        df = sAs.GetInstance.GetDataCollector().FetchStockInformation(ctx, '')
        if df is None or len(df) == 0:
            return False
        return sAs.GetInstance.GetDataCenterDB().DataFrameToDB('StockInformation', df)

    # --------------------------- Annual Reprot ---------------------------

    def __get_annual_report(self, stock_code: str, annual_report_type: str, condition: str) -> pd.DataFrame:
        # 1.Query
        result = self.__query_annual_report(annual_report_type, condition)
        if result is not None and len(result) > 0:
            return result.get(stock_code, None)

        # 2.Download
        ar_dict = self.__download_annual_report(stock_code, annual_report_type)
        if ar_dict is None or not isinstance(ar_dict, dict):
            print('__download_annual_report() : Wrong result - ', type(ar_dict))
            return None
        report = ar_dict.get(annual_report_type, None)
        if report is None:
            print('__get_annual_report() - Fail.')
            return None

        # 3.Format
        report = self.__check_format_downloaded_annual_report(report)
        if report is None:
            print('__check_format_downloaded_annual_report() - Error format of annual report and cannot recover.')
            return None

        # 4.Save
        self.__save_annual_report(stock_code, report, annual_report_type)

        return report

    def __query_annual_report(self, annual_report_table: str, condition: str) -> {str: pd.DataFrame}:
        annual_report = sAs.GetInstance.GetDataCenterDB().DataFrameFromDB(
            annual_report_table, DataCenterCore.FINANCIAL_STATEMENTS_FIELDS, condition)
        if annual_report is None or len(annual_report) == 0:
            return None
        return self.__json_df_to_annual_df(annual_report)

    @staticmethod
    def __download_annual_report(stock_code: str, annual_report_type: str) -> {str: pd.DataFrame}:
        ctx = data_collector.FetchContext()
        return sAs.GetInstance.GetDataCollector().FetchStockAnnualReport(ctx, stock_code, [annual_report_type, ])

    @staticmethod
    def __check_format_downloaded_annual_report(annual_report: pd.DataFrame) -> pd.DataFrame:
        if annual_report is None:
            return None

        # Check index: it should be year digit str.
        index_format = []
        index = annual_report.index.tolist()
        for i in index:
            if not isinstance(i, int) and not isinstance(i, str):
                return None
            if i is int:
                i = str(i)
            elif '-' in i:
                i = i.split('-')[0]
            if not i.isdigit():
                i = ''
                print('__check_format_downloaded_annual_report() - Warning: Invalid index : ', i)
            index_format.append(i)
        annual_report.index = index_format

        # Standardize columns
        columns = annual_report.columns.tolist()
        columns = sAs.GetInstance.GetAliasesTable().Standardize(columns)
        annual_report.columns = columns

        # Remove empty row
        annual_report = annual_report.loc[annual_report.index != '']
        annual_report.to_csv('D:/test.csv')

        return annual_report


    # Not use EAV, use JSON.
    def __save_annual_report(self, stock_code: str, annual_report: pd.DataFrame, annual_report_table: str) -> bool:
        if annual_report is None:
            return False
        df_json = self.__annual_df_2_json_df(stock_code, annual_report)
        if df_json is None or len(df_json) == 0:
            return False
        # Not need to insert serial number
        df_json.columns = DataCenterCore.FINANCIAL_STATEMENTS_FIELDS
        ret = self.__del_annual_report(stock_code, [], [annual_report_table]) and \
                sAs.GetInstance.GetDataCenterDB().DataFrameToDB(annual_report_table, df_json, 'append')
        return ret

    @staticmethod
    def __del_annual_report(stock_code: str, annuals: [int], tables: [str]) -> bool:
        ret = True
        years = ','.join([str(y) for y in annuals])
        condition = "StockCode = '" + stock_code + "'"
        if years != '':
            condition +=  ' AND AccountingAnnual IN (' + years + ')'
        for table in tables:
            ret &= sAs.GetInstance.GetDataCenterDB().ExecuteDelete(table, condition)
        return ret

    # df <-> json
    @staticmethod
    def __annual_df_2_json_df(stock_code: str, df: pd.DataFrame) -> pd.DataFrame:
        lines = []
        columns = df.columns.tolist()
        columns = sAs.GetInstance.GetAliasesTable().Standardize(columns)
        for index, row in df.iterrows():
            line = []
            year = index.split('-')[0]
            line.append(stock_code)                 # The 1st column
            line.append(year)                       # The 2nd column
            properties = {}
            for r, c in zip(row, columns):
                properties[c] = r
            line.append(json.dumps(properties))     # The 3rd column
            lines.append(line)
        return pd.DataFrame(lines)

    @staticmethod
    def __json_df_to_annual_df(df_json: pd.DataFrame) -> {str: pd.DataFrame}:
        if DataCenterCore.FINANCIAL_STATEMENTS_FIELDS[0] not in df_json.columns or\
            DataCenterCore.FINANCIAL_STATEMENTS_FIELDS[1] not in df_json.columns or\
                DataCenterCore.FINANCIAL_STATEMENTS_FIELDS[2] not in df_json.columns:
            return None
        df_trim = df_json[[DataCenterCore.FINANCIAL_STATEMENTS_FIELDS[0],       # StockCode -> #0
                           DataCenterCore.FINANCIAL_STATEMENTS_FIELDS[1],       # AccountingAnnual -> #1
                           DataCenterCore.FINANCIAL_STATEMENTS_FIELDS[2]]]      # FinancialData -> #2
        map_df_stocks = {}
        for index, row in df_trim.iterrows():
            stock_code = row[0]
            accounting_annual = row[1]
            financial_data = row[2]

            properties = json.loads(financial_data)
            properties['AccountingAnnual'] = accounting_annual
            df_line = pd.DataFrame(properties, index=['properties'])

            if map_df_stocks.get(stock_code, None) is not None:
                map_df_stocks[stock_code] = map_df_stocks[stock_code].append(df_line)
            else:
                map_df_stocks[stock_code] = df_line

        for k in map_df_stocks.keys():
            df_ref = map_df_stocks.get(k)
            df_ref.set_index('AccountingAnnual', inplace=True, drop=True)
            df_ref.columns = sAs.GetInstance.GetAliasesTable().Readablize(df_ref.columns.tolist())
        return map_df_stocks


class DataCenter:
    def __init__(self):
        self.__core = DataCenterCore()
        # {stock_code: {table_name, df}}
        self.__cache_annual_report = {}

    def Init(self) -> bool:
        return self.__core.Init()

    def CacheAnnualReportData(self, stock_codes: [str]):
        for stock in stock_codes:
            self.__cache_annual_report[stock] = \
                self.__core.GetStockAnnualReportData(
                stock, 0, 0, public.constant.ANNUAL_REPORT_TYPES)

    # return -> {year, value}
    def GetStockAnnualReportDataSerial(self, stock_code: str, accounting: str, years: [int]) -> {int: float}:
        pass

    # return -> {StockCode, DataFrame}
    def GetStockAnnualReportDataTable(self, stock_codes: [str], accounting: [str], years: [int] = []) -> {str: pd.DataFrame}:
        ret = {}
        if isinstance(stock_codes, str):
            stock_codes = [stock_codes, ]
        account_s = sAs.GetInstance.GetAliasesTable().Standardize(accounting)
        for stock in stock_codes:
            if len(accounting) > 0:
                df_stock = pd.DataFrame(columns=account_s)
            else:
                df_stock = None
            for report_type in public.constant.ANNUAL_REPORT_TYPES:
                report = self.__get_cached_stock_annual_report(stock, report_type)
                if report is None:
                    self.CacheAnnualReportData([stock, ])
                report = self.__get_cached_stock_annual_report(stock, report_type)
                if report is not None:
                    if len(years) != 0:
                        report = report.loc[[str(y) for y in years]]
                    if df_stock is not None:
                        public.common.DataFrameColumnCopy(report, df_stock, account_s)
                    else:
                        df_stock = report
            if len(accounting) > 0:
                df_stock.columns = accounting
            else:
                df_stock.columns = sAs.GetInstance.GetAliasesTable().Readablize(df_stock.columns.tolist())
            if len(years) != 0:
                df_stock.index = years
            ret[stock] = df_stock
        return ret

    # --------------------------------------- private ---------------------------------------

    def __get_cached_stock_data(self, stock_code: str) -> {str: pd.DataFrame}:
        return self.__cache_annual_report.get(stock_code, None)

    # report_type -> public.constant.ANNUAL_REPORT_TYPES
    def __get_cached_stock_annual_report(self, stock_code: str, report_type: str) -> pd.DataFrame:
        tables = self.__cache_annual_report.get(stock_code, None)
        if tables is None:
            return None
        return tables.get(report_type, None)

    # For test
    @staticmethod
    def SubAnnualReportTable(df: pd.DataFrame, years: [int], accounting: [str]) -> pd.DataFrame:
        return DataCenter.__sub_annual_report_table(df, years, accounting)

    @staticmethod
    def __sub_annual_report_table(df: pd.DataFrame, years: [int], accounting: [str]) -> pd.DataFrame:
        df_sub = pd.DataFrame()
        for a in accounting:
            if a not in df.columns:
                serial = np.empty(df.shape[0])
                serial.fill(np.nan)
            else:
                serial = df[a]
            df_sub.insert(len(df_sub.columns), a, serial)
        return df_sub.loc[years]

