import pandas as pd
from datetime import date

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import config
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Analyzer.AnalyzerUtility import *
    from DataHub.DataHubEntry import DataHubEntry
    from Database.DatabaseEntry import DatabaseEntry
except Exception as e:
    sys.path.append(root_path)

    import config
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Analyzer.AnalyzerUtility import *
    from DataHub.DataHubEntry import DataHubEntry
    from Database.DatabaseEntry import DatabaseEntry
finally:
    pass


# ------------------------------------------------------ 01 - 05 -------------------------------------------------------

def analysis_black_list(securities: str, data_hub: DataHubEntry,
                        database: DatabaseEntry, context: AnalysisContext) -> AnalysisResult:
    nop(data_hub)

    if context.cache.get('black_table', None) is None:
        context.cache['black_table'] = database.get_black_table().get_name_table()
    black_table = context.cache.get('black_table', None)

    df_slice = black_table[black_table['name'] == securities]
    exclude = len(df_slice) > 0
    if exclude:
        reason = get_dataframe_slice_item(df_slice, 'reason', 0, '')
    else:
        reason = '不在黑名单中'
    return AnalysisResult(securities, not exclude, reason)


def analysis_less_than_3_years(securities: str, data_hub: DataHubEntry,
                               database: DatabaseEntry, context: AnalysisContext) -> AnalysisResult:
    nop(database)

    if context.cache.get('securities_info', None) is None:
        context.cache['securities_info'] = data_hub.get_data_center().query('Market.SecuritiesInfo')
    df = context.cache.get('securities_info', None)

    df_slice = df[df['stock_identity'] == securities]
    listing_date = get_dataframe_slice_item(df_slice, 'listing_date', 0, now())
    exclude = now().year - listing_date.year < 3
    reason = '上市日期' + str(listing_date) + ('小于三年' if exclude else '大于三年')
    return AnalysisResult(securities, not exclude, reason)


def analysis_location_limitation(securities: str, data_hub: DataHubEntry,
                                 database: DatabaseEntry, context: AnalysisContext) -> AnalysisResult:
    nop(database)

    if context.cache.get('securities_info', None) is None:
        context.cache['securities_info'] = data_hub.get_data_center().query('Market.SecuritiesInfo')
    df = context.cache.get('securities_info', None)

    df_slice = df[df['stock_identity'] == securities]
    area = get_dataframe_slice_item(df_slice, 'area', 0, '')
    exclude = area in ['黑龙江', '辽宁', '吉林']
    reason = securities + '地域为' + str(area)
    return AnalysisResult(securities, not exclude, reason)


def analysis_finance_report_sign(securities: str, data_hub: DataHubEntry,
                                 database: DatabaseEntry, context: AnalysisContext) -> AnalysisResult:
    nop(database)

    if context.cache.get('finance_audit', None) is None:
        context.cache['finance_audit'] = data_hub.get_data_center().query('Finance.Audit')
    df = context.cache.get('finance_audit', None)

    error_report = check_gen_report_when_data_missing(df, securities, 'Finance.IncomeStatement',
                                                      ['stock_identity', 'period', 'conclusion'])
    if error_report is not None:
        return error_report

    df_slice = df[df['stock_identity'] == securities]
    df_slice_in_4_years = df_slice[df_slice['period'] > years_ago(4)]

    score = 100
    reason = []

    for index, row in df_slice_in_4_years.iterrows():
        period = row['period']
        conclusion = row['conclusion']

        if conclusion != '标准无保留意见':
            score = 0
            reason.append(date2text(period) + ' : ' + conclusion)
    if len(reason) == 0:
        reason.append('近四年均为标准无保留意见')

    # df_slice.sort_values('period', ascending=True)
    #
    # if len(df_slice) == 1:
    #     print('Too less record: ' + securities)
    # df_slice_in_3_years = df_slice[df_slice['period'] > years_ago(3)]
    #
    # conclusion_all = df_slice['conclusion']
    # conclusion_all_list = conclusion_all.to_list()
    #
    # conclusion_3_years = df_slice_in_3_years['conclusion']
    # conclusion_3_years_list = conclusion_3_years.to_list()

    # ok_count = 0
    # nok_count = 0
    # for conclusion in conclusion_all_list:
    #     if conclusion != '标准无保留意见':
    #         nok_count += 1
    #     else:
    #         ok_count += 1
    # score = 100 * ok_count / (ok_count + nok_count) if (ok_count + nok_count) > 0 else 100
    #
    # for conclusion in conclusion_3_years_list:
    #     if conclusion != '标准无保留意见':
    #         score = 0
    #         break

    # agency = get_dataframe_slice_item(df_slice, 'agency', 0, '')
    # sign = get_dataframe_slice_item(df_slice, 'sign', 0, '')

    # reason = '标准无保留意见' if score == 100 else '存在非标意见'

    return AnalysisResult(securities, score, reason)


def analysis_exclude_industries(securities: str, data_hub: DataHubEntry,
                                database: DatabaseEntry, context: AnalysisContext) -> AnalysisResult:
    nop(database)

    if context.cache.get('securities_info', None) is None:
        context.cache['securities_info'] = data_hub.get_data_center().query('Market.SecuritiesInfo')
    df = context.cache.get('securities_info', None)

    df_slice = df[df['stock_identity'] == securities]
    error_report = check_gen_report_when_data_missing(df_slice, securities, 'Finance.IncomeStatement',
                                                      ['industry'])
    if error_report is not None:
        return error_report

    industry = get_dataframe_slice_item(df_slice, 'industry', 0, '')
    exclude = industry in ['种植业', '渔业', '林业', '畜禽养殖', '农业综合']
    reason = '所在行业[' + str(industry) + (']属于农林牧渔' if exclude else ']不属于农林牧渔')
    return AnalysisResult(securities, not exclude, reason)


# ------------------------------------------------------ 05 - 10 -------------------------------------------------------

def analysis_consecutive_losses(securities: str, data_hub: DataHubEntry,
                                database: DatabaseEntry, context: AnalysisContext) -> AnalysisResult:
    nop(database)
    nop(context)

    df = data_hub.get_data_center().query('Finance.IncomeStatement', securities)
    error_report = check_gen_report_when_data_missing(df, securities, 'Finance.IncomeStatement',
                                                      ['period', 'total_profit', 'operate_profit'])
    if error_report is not None:
        return error_report

    df.fillna(0.0, inplace=True)
    df_in_4_years = df[df['period'] > years_ago(4)]
    df_in_4_years.sort_values('period', ascending=True)

    score = 100
    reason = []
    for index, row in df_in_4_years.iterrows():
        period = row['period']
        # 利润总额
        total_profit = row['total_profit']
        # 营业利润
        operating_profit = row['operate_profit']

        if total_profit < 0:
            score = 0
            reason.append(date2text(period) + '：利润总额 - ' + str(total_profit))
        if operating_profit < 0:
            score = 0
            reason.append(date2text(period) + '：营业利润 - ' + str(operating_profit))
    if len(reason) == 0:
        reason.append('近四年不存在亏损')

    return AnalysisResult(securities, score, reason)


def analysis_profit_structure(securities: str, data_hub: DataHubEntry,
                              database: DatabaseEntry, context: AnalysisContext) -> AnalysisResult:
    nop(database)
    nop(context)

    df = data_hub.get_data_center().query('Finance.IncomeStatement', securities)
    error_report = check_gen_report_when_data_missing(df, securities, 'Finance.IncomeStatement',
                                                      ['period', 'revenue', 'total_revenue', 'oth_b_income'])
    if error_report is not None:
        return error_report

    df.fillna(0.0, inplace=True)
    df_in_4_years = df[df['period'] > years_ago(4)]
    df_in_4_years.sort_values('period', ascending=True)

    score = 100
    reason = []
    for index, row in df_in_4_years.iterrows():
        period = row['period']
        # 营业收入
        operating_profit = row['revenue']
        # 营业总收入(为什么和营业收入是一样的)
        total_revenue = row['total_revenue']
        # 其他业务收入
        other_revenue = row['oth_b_income']

        print('总%s - 营%s - 它%s' % (total_revenue, operating_profit, other_revenue))
        main_operating_profit_ratio = float(operating_profit - other_revenue) / operating_profit

        if main_operating_profit_ratio > 50:
            score = 0
            reason.append(period + (': 主营业务收入：%s；营业总收入：%s；占比：%s' %
                                    (operating_profit - other_revenue, operating_profit, main_operating_profit_ratio)))

    return AnalysisResult(securities, score, reason)


def analysis_cash_loan_both_high(securities: str, data_hub: DataHubEntry,
                                 database: DatabaseEntry, context: AnalysisContext) -> AnalysisResult:
    nop(database)
    nop(context)

    fields_balance_sheet = ['短期借款', '长期借款', '货币资金', '其他流动资产',  '应付债券',
                            '一年内到期的非流动负债', '应收票据', '其他流动负债', '流动负债合计',
                            '资产总计']
    fields_income_statement = ['净利润(含少数股东损益)', '减:财务费用']

    assert data_hub.get_data_center().check_readable_name(fields_balance_sheet)
    assert data_hub.get_data_center().check_readable_name(fields_income_statement)

    df_balance_sheet = data_hub.get_data_center().query(
        'Finance.BalanceSheet', securities, (years_ago(4), now()),
        fields=fields_balance_sheet + ['stock_identity', 'period'], readable=True)
    df_income_statement = data_hub.get_data_center().query(
        'Finance.IncomeStatement', securities, (years_ago(4), now()),
        fields=fields_income_statement + ['stock_identity', 'period'], readable=True)

    df = pd.merge(df_balance_sheet, df_income_statement, how='left', on=['stock_identity', 'period'])

    df.fillna(0.0, inplace=True)
    df.sort_values('period', ascending=True)

    score = 100
    reason = []
    applied = False
    for index, row in df.iterrows():
        period = row['period']

        if row['流动负债合计'] < 0.001:
            reason.append(str(period) + ': 流动负债合计为0，可能数据缺失')
            continue
        applied = True

        cash = row['货币资金'] + row['其他流动资产']
        loan = row['短期借款'] + row['长期借款'] + row['一年内到期的非流动负债'] + row['应付债券'] + row['其他流动负债']
        loan_vs_totol_asset = loan / row['资产总计']
        fin_fee_vs_benefit = row['减:财务费用'] / row['净利润(含少数股东损益)']

        # 货币资金+其他流动资产 > 短期借款+长期借款+一年到期的非流动负债+应付债券
        # 贷款占资产总额的比例大于30%
        # 利息费用与净利润比例大于30%
        if cash > loan and loan_vs_totol_asset > 0.3 and fin_fee_vs_benefit > 0.3:
            score = 0
            reason.append('%s: 资金：%s；借款：%s。贷款比总资产比例：%s。利息比净利润%s' %
                          (period, cash, loan, loan_vs_totol_asset, fin_fee_vs_benefit))

    return AnalysisResult(securities, score, reason) if applied else \
        AnalysisResult(securities, AnalysisResult.SCORE_NOT_APPLIED, reason)


# ----------------------------------------------------------------------------------------------------------------------

METHOD_LIST = [
    ('7a2c2ce7-9060-4c1c-bca7-71ca12e92b09', '黑名单',       '排除黑名单中的股票',         analysis_black_list),
    ('e639a8f1-f2f5-4d48-a348-ad12508b0dbb', '不足三年',     '排除上市不足三年的公司',     analysis_less_than_3_years),
    ('f39f14d6-b417-4a6e-bd2c-74824a154fc0', '地域限制',     '排除特定地域的公司',         analysis_location_limitation),
    ('3b01999c-3837-11ea-b851-27d2aa2d4e7d', '财报非标',     '排除财报非标的公司',         analysis_finance_report_sign),
    ('1fdee036-c7c1-4876-912a-8ce1d7dd978b', '农林牧渔',     '排除农林牧渔相关行业',       analysis_exclude_industries),

    ('b0e34011-c5bf-4ac3-b6a4-c15e5ea150a6', '连续亏损',     '排除营业利润或利润总额连续亏损的公司', analysis_consecutive_losses),
    # oth_b_income field missing for lots of securities. This analyzer may not work.
    ('d811ebd6-ee28-4d2f-b7e0-79ce0ecde7f7', '非主营业务',   '排除主营业务或营业利润占比过低的公司（数据缺失）', analysis_profit_structure),
    ('2c05bb4c-935e-4be7-9c04-ae12720cd757', '存贷双高',     '排除存贷双高的公司',         analysis_cash_loan_both_high),
    ('e6ab71a9-0c9f-4500-b2db-d682af567f70', '商誉过高',     '排除商誉过高的公司',         None),
    ('4ccedeea-b731-4b97-9681-d804838e351b', '股权质押过高', '', None),
    ('f6fe627b-acbe-4b3f-a1fb-5edcd00d27b0', '', '', None),
]


def plugin_prob() -> dict:
    return {
        'plugin_id': '7b59e0e4-5572-4cd8-8982-baa94f8af3d9',
        'plugin_name': 'basic_finance_analysis',
        'plugin_version': '0.0.0.1',
        'tags': ['finance', 'analyzer'],
        'methods': METHOD_LIST,
    }


def plugin_adapt(method: str) -> bool:
    return method in methods_from_prob(plugin_prob())


def plugin_capacities() -> list:
    return [
        'exclusive',
    ]


# ----------------------------------------------------------------------------------------------------------------------

def analysis(securities: [str], methods: [str], data_hub: DataHubEntry,
             database: DatabaseEntry, extra: dict) -> [AnalysisResult]:
    return standard_dispatch_analysis(securities, methods, data_hub, database, extra, METHOD_LIST)


















