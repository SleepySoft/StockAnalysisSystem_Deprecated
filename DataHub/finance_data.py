import traceback
import pandas as pd

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import DataHub.DataUtility as DataUtility
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Utiltity.plugin_manager import PluginManager
    from Database.DatabaseEntry import DatabaseEntry
    from Database.UpdateTableEx import UpdateTableEx
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    import DataHub.DataUtility as DataUtility
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Utiltity.plugin_manager import PluginManager
    from Database.DatabaseEntry import DatabaseEntry
    from Database.UpdateTableEx import UpdateTableEx
    from Utiltity.plugin_manager import PluginManager
finally:
    logger = logging.getLogger('')


"""
We don't need to specify the filed currently. Just using the alias table.
If we want to standardize the field. Just rename all the fields.
"""


NEED_COLLECTOR_CAPACITY = ['BalanceSheet', 'CashFlowStatement', 'IncomeStatement']
ROOT_TAGS = ['BalanceSheet', 'CashFlowStatement', 'IncomeStatement']

TABLE_BALANCE_SHEET = 'BalanceSheet'
TABLE_CASH_FLOW_STATEMENT = 'CashFlowStatement'
TABLE_INCOME_STATEMENT = 'IncomeStatement'

IDENTITY_FINANCE_DATA = '<stock_code>.<exchange>'

QUERY_FIELD = {
    'content':          ([str], ROOT_TAGS),
    'stock_identity':   ([str], []),
    # 'report_type':      ([str], ['ANNUAL', 'SEMIANNUAL', 'QUARTERLY', 'MONTHLY', 'WEEKLY']),
    'since':            ([datetime.datetime, None], []),
    'until':            ([datetime.datetime, None], [])}

RESULT_FIELD = {
    'identity':         ([str], []),
    'period':           ([int], [])}                # The last day of report period


class FinanceData(DataUtility.DataUtility):
    def __init__(self, plugin: PluginManager, update: UpdateTableEx):
        super().__init__(plugin, update)
        self.__cached_data = {}
        self.__save_list = []
        # self.__load_cached_data()

    # ---------------------------------------------------------------------------------x--------------------------------

    def execute_update_patch(self, patches: [DataUtility.Patch]) -> DataUtility.RESULT_CODE:
        logger.info('FinanceData.execute_update_patch(' + str(patches) + ')')

        for patch in patches:
            if not self.is_data_support(patch.tags):
                logger.info('FinanceData.execute_update_patch() - Data is not support.')
                return DataUtility.RESULT_NOT_SUPPORTED

            report_type = patch.tags[0]
            stock_identity = normalize_stock_identity(patch.tags[1])
            df = self.__do_fetch_finance_data(report_type, stock_identity, patch.since, patch.until)
            if df is None or len(df) == 0:
                return DataUtility.RESULT_FAILED

            df.set_index('year')
            codes = df['code'].unique()
            for code in codes:
                new_df = df[df['code'] == code]
                if new_df is None or len(new_df) == 0:
                    continue
                if code in self.__cached_data.keys():
                    concat_dataframe_by_index([self.__cached_data[code], new_df])
                else:
                    self.__cached_data[code] = [new_df]
                self.__save_list.append(code)
        return DataUtility.RESULT_SUCCESSFUL

    def execute_batch_update(self) -> DataUtility.RESULT_CODE:
        nop(self)
        logger.info('SecuritiesInfo.execute_batch_update()')
        return self.execute_single_update([])

    def trigger_save_data(self, tags: [str]) -> DataUtility.RESULT_CODE:
        result = self.__save_cached_data()
        if result:
            self.get_update_table().update_latest_update_time('SecuritiesInfo', '', '')
            return DataUtility.RESULT_SUCCESSFUL
        return DataUtility.RESULT_FAILED

    # -------------------------------------------------- probability --------------------------------------------------

    def get_root_tags(self) -> [str]:
        nop(self)
        return NEED_COLLECTOR_CAPACITY

    def is_data_support(self, tags: [str]) -> bool:
        nop(self)
        return (tags is not None) and (isinstance(tags, list)) and (len(tags) > 2) and (tags[0] in ROOT_TAGS)

    def get_cached_data_range(self, tags: [str]) -> (datetime.datetime, datetime.datetime):
        if not self.is_data_support(tags):
            return None, None
        df = self.__cached_data.get(tags[0])
        if df is None or len(df) == 0:
            return None, None
        min_date = min(df['trade_date'])
        max_date = max(df['trade_date'])
        return text_auto_time(min_date), text_auto_time(max_date)

    # --------------------------------------------------- private if ---------------------------------------------------

    def data_from_cache(self, selectors: DataUtility.Selector or [DataUtility.Selector]) -> pd.DataFrame or None:
        nop(selectors)
        return None

    # -------------------------------------------------- probability --------------------------------------------------

    def get_reference_data_range(self, tags: [str]) -> (datetime.datetime, datetime.datetime):
        nop(self, tags)
        return [None, None]

    # -----------------------------------------------------------------------------------------------------------------

    def __do_fetch_finance_data(self, report_type: str, stock_identity: str,
                                report_since: datetime.datetime, report_until: datetime.datetime) -> pd.DataFrame:
        if report_type not in ROOT_TAGS:
            return None
        argv = {
                'content':          report_type,
                'stock_identity':   stock_identity,
                'since':            report_since,
                'until':            report_until,
            }
        if not self._check_dict_param(argv, QUERY_FIELD):
            return None
        plugins = self.get_plugin_manager().find_module_has_capacity(report_type)
        for plugin in plugins:
            df = self.get_plugin_manager().execute_module_function(plugin, 'fetch_data', argv)

            if df is None or not isinstance(df, pd.DataFrame) or len(df) == 0 or \
                    not self._check_dataframe_field(df, RESULT_FIELD, list(RESULT_FIELD.keys())):
                logger.info('Finance data - Fetch data format Error.')
                continue
            return df
        return None

    def __load_cached_data(self) -> bool:
        pass
        # table = DataTable().get_securities_table()
        # record = table.query()
        # if record is not None and len(record) > 0:
        #     self.__cached_data = pd.DataFrame(record)
        #     del self.__cached_data['DateTime']
        #     del self.__cached_data['_id']
        # else:
        #     self.__cached_data = pd.DataFrame(column=list(FIELD_INFO.keys()))
        # return True

    def __save_cached_data(self) -> bool:
        pass
        # table = DataTable().get_securities_table()
        # for index, row in self.__cached_data.iterrows():
        #     code = row['code']
        #     exchange = row['exchange']
        #     identity = IDENTITY_SECURITIES_INFO.\
        #         replace('<stock_code>', code).\
        #         replace('<exchange>', exchange)
        #     table.upsert(identity, text_auto_time('2000-01-01'), row.to_dict())
        # return True


# ----------------------------------------------------- Test Code ------------------------------------------------------


def __build_instance() -> FinanceData:
    plugin_path = root_path + '/Collector/'

    collector_plugin = PluginManager(plugin_path)
    collector_plugin.refresh()

    update_table = UpdateTableEx()

    return FinanceData(collector_plugin, update_table)


def test_basic_feature():
    fd = __build_instance()

    df = fd.query_data(['BalanceSheet', '600000', 'ANNUAL'])
    print('----------------------------------------------------------------------------------------------')
    print(df)

    df = fd.query_data(['CashFlowStatement', '600000', 'ANNUAL'])
    print('----------------------------------------------------------------------------------------------')
    print(df)

    df = fd.query_data(['IncomeStatement', '600000', 'ANNUAL'])
    print('----------------------------------------------------------------------------------------------')
    print(df)


def test_entry():
    test_basic_feature()


# ----------------------------------------------------- File Entry -----------------------------------------------------

def main():
    test_entry()

    # If program reaches here, all test passed.
    print('All test passed.')


# ------------------------------------------------- Exception Handling -------------------------------------------------

def exception_hook(type, value, tback):
    # log the exception here
    print('Exception hook triggered.')
    print(type)
    print(value)
    print(tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)


sys.excepthook = exception_hook


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass







