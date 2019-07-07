import sys
import traceback
import pandas as pd
import datetime

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Database import UpdateTableEx
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Database import UpdateTableEx
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
finally:
    logger = logging.getLogger('')


PYTHON_DATAFRAME_TYPE_MAPPING = {
    'str': 'object',
    'int64': 'object',
    'datetime': 'datetime64[ns]',
}


class DataUtility:

    RESULT_CODE = object
    RESULT_FALSE = False
    RESULT_TRUE = True
    RESULT_SUCCESSFUL = 2
    RESULT_FAILED = 4
    RESULT_NOT_SUPPORTED = 8
    RESULT_NOT_IMPLEMENTED = None

    UPDATE_LAZY = 1
    UPDATE_BATCH = 2
    UPDATE_MANUAL = 3
    UPDATE_OFFLINE = 4

    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, plugin: PluginManager, update: UpdateTableEx):
        self.__plugin = plugin
        self.__update = update
        self.__update_strategy = DataUtility.UPDATE_LAZY

    def get_update_table(self) -> UpdateTableEx:
        return self.__update

    def get_plugin_manager(self) -> PluginManager:
        return self.__plugin

    def set_update_strategy(self, strategy: int):
        self.__update_strategy = strategy

    def get_update_strategy(self) -> int:
        return self.__update_strategy

    # --------------------------------------------------- public if ---------------------------------------------------

    def query_data(self, tags: [str],
                   timeval: (datetime.datetime, datetime.datetime) = None,
                   extra: dict = None) -> pd.DataFrame:
        logger.info('DataUtility.query_data(' + str(tags) + ', ' + str(timeval) + ', ' + str(extra) + ')')
        _tags = self.__normalize_tags(tags)
        need_update, update_since, update_until = self.check_update(_tags)
        if need_update == DataUtility.RESULT_TRUE:
            if self.__update_strategy == DataUtility.UPDATE_LAZY:
                result = self.execute_single_update(_tags, (update_since, update_until))
            elif self.__update_strategy == DataUtility.UPDATE_BATCH:
                result = self.execute_batch_update()
            else:
                result = DataUtility.RESULT_NOT_IMPLEMENTED
                logger.info('Unsupported update strategy: ' + str(self.__update_strategy))
            if result == DataUtility.RESULT_SUCCESSFUL:
                self.trigger_save_data(tags)
        else:
            logger.info('Not need update for : ' + str(tags))
        return self.data_from_cache(_tags, timeval, extra)

    def check_update(self, tags: [str]) -> [(str, datetime, datetime)]:
        """
        Check whether the tag specified data need update.
        Update strategy:
            0.ref_since is reserved
            1.latest update is None => Never been updated
                ->  Update all (patch_since = None, patch_until = None).
            2.ref_until is not None => Apply data range check
                -> If prev_until is None => Should be an error, update all (patch_since = None, patch_until = None).
                -> If prev_until less than ref_until => Update (since = tomorrow of previous until, until = ref_until)
                -> Else => Not need to update
            3.ref_until is None => Apply latest update check
                -> ref_latest_update is None => Should be an error, update all (patch_since = None, patch_until = None).
                -> latest_update < ref_until => Update (since = tomorrow of latest update, until = today)
                -> Else => Not need to update
        :param tags: The tags to identify the data
        :return: List of Tuple: [(
            patch_tag :   The data patch should apply to.
            patch_since : The data we need update since.
            patch_until : The data we need update until.
            )]
        """
        logger.info('DataUtility.check_update(' + str(tags) + ')')

        if self.__update_strategy == DataUtility.UPDATE_MANUAL:
            logger.info('  | MANUAL - Return False')
            return DataUtility.RESULT_FALSE
        if self.__update_strategy == DataUtility.UPDATE_OFFLINE:
            logger.info('  | OFFLINE - Return False')
            return DataUtility.RESULT_FALSE

        latest_update = self._get_data_last_update(tags)
        if latest_update is None:
            return [(tags, None, None)]

        ref_since, ref_until = self.get_reference_data_range(tags)
        if ref_until is not None:
            since, until = self.get_cached_data_range(tags)
            if until is None:
                logger.error('DataUtility.check_update: until is None. Update all.')
                return [(tags, None, None)]
            elif until < ref_until:
                return [(tags, tomorrow_of(until), ref_until)]
            else:
                logger.info('DataUtility.check_update: Check data range - Not need update.')
                return []
        else:
            ref_latest_update = self.get_reference_last_update()
            if ref_latest_update is None:
                logger.error('DataUtility.check_update: ref_latest_update is None. Update all.')
                return [(tags, None, None)]
            elif latest_update < ref_latest_update:
                return [(tags, tomorrow_of(latest_update), ref_latest_update)]
            else:
                logger.info('DataUtility.check_update: Check latest update - Not need update.')
                return []
        logger.error('DataUtility.check_update: Never reach here.')
        return []

    def execute_single_update(self, tags: [str], timeval: (datetime.datetime, datetime.datetime) = None) -> RESULT_CODE:
        nop(self)
        logger.info('DataUtility.execute_single_update(' + str(tags) + ') -> RESULT_NOT_IMPLEMENTED')
        return DataUtility.RESULT_NOT_IMPLEMENTED

    def execute_batch_update(self) -> RESULT_CODE:
        nop(self)
        logger.info('DataUtility.execute_batch_update() -> RESULT_NOT_IMPLEMENTED')
        return DataUtility.RESULT_NOT_IMPLEMENTED

    def trigger_save_data(self, tags: [str]) -> RESULT_CODE:
        nop(self)
        logger.info('DataUtility.trigger_save_data(' + str(tags) + ') -> RESULT_NOT_IMPLEMENTED')
        return DataUtility.RESULT_NOT_IMPLEMENTED

    # --------------------------------------------------- private if ---------------------------------------------------

    def data_from_cache(self, tags: [str],
                        timeval: (datetime.datetime, datetime.datetime),
                        extra: dict = None) -> pd.DataFrame:
        logger.info('DataUtility.data_from_cache(' + str(tags) + ') -> RESULT_NOT_IMPLEMENTED')
        return DataUtility.RESULT_NOT_IMPLEMENTED

    # -------------------------------------------------- probability --------------------------------------------------

    def get_root_tags(self) -> [str]:
        nop(self)
        return []

    def is_data_support(self, tags: [str]) -> bool:
        nop(self, tags)
        return False

    def get_cached_data_range(self, tags: [str]) -> (datetime.datetime, datetime.datetime):
        _tags = self.__normalize_tags(tags)
        return self.get_update_table().get_since_until(*_tags)

    def get_cache_last_update(self, tags: [str]) -> datetime.datetime:
        _tags = self.__normalize_tags(tags)
        return self.get_update_table().update_latest_update_time(*_tags)

    def get_reference_data_range(self, tags: [str]) -> (datetime.datetime, datetime.datetime):
        nop(self, tags)
        return [None, yesterday()]

    def get_reference_last_update(self, tags: [str]) -> datetime.datetime:
        nop(self, tags)
        return today()

    # --------------------------------------------------- assistance ---------------------------------------------------

    def _get_data_range(self, tags: list) -> (datetime.datetime, datetime.datetime):
        _tags = self.__normalize_tags(tags)
        return self.__update.get_since(*_tags), self.__update.get_until(*tags)

    def _get_data_last_update(self, tags: list) -> datetime.datetime:
        _tags = self.__normalize_tags(tags)
        return self.__update.get_last_update_time(*_tags)

    def _cache_data_satisfied(self, tags: list, since: datetime.datetime, until: datetime.datetime) -> bool:
        _tags = self.__normalize_tags(tags)
        _since, _until = self._get_data_range(_tags)
        return since >= _since and until <= _until

    def _update_time_record(self, tags: [str], df: pd.DataFrame, time_field: str):
        if len(df) == 0:
            return
        _tags = self.__normalize_tags(tags)
        min_date = min(df[time_field])
        max_date = max(df[time_field])
        if min_date is not None:
            self.get_update_table().update_since(*_tags, min_date)
        if max_date is not None:
            self.get_update_table().update_until(*_tags, max_date)
        self.get_update_table().update_latest_update_time(*_tags)

    # def _check_update_by_range(self, tags: [str]) -> (RESULT_CODE, datetime, datetime):
    #     ref_since, ref_until = self.get_reference_data_range(tags)
    #     if ref_since is None and ref_until is None:
    #         return DataUtility.RESULT_NOT_SUPPORTED, None, None
    #
    #     need_update = DataUtility.RESULT_FALSE
    #     update_since, update_until = None, None
    #     since, until = self.get_cached_data_range(tags)
    #
    #     if ref_since is not None:
    #         if since is None or since > ref_since:
    #             update_since = ref_since
    #             need_update = DataUtility.RESULT_TRUE
    #     if ref_until is not None:
    #         if until is None or until < ref_until:
    #             update_until = ref_until
    #             need_update = DataUtility.RESULT_TRUE
    #
    #     if update_since is None and until is not None:
    #         update_since = tomorrow_of(until)
    #     if update_until is None and since is not None:
    #         update_until = yesterday_of(since)
    #
    #     if update_since is not None and update_until is not None and update_since >= update_until:
    #         need_update = DataUtility.RESULT_FALSE
    #     return need_update, update_since, update_until
    #
    # def _check_update_by_last_update(self, tags: [str]) -> (RESULT_CODE, datetime, datetime):
    #     reference_last_update = self.get_reference_last_update(tags)
    #     if reference_last_update is None:
    #         return DataUtility.RESULT_NOT_SUPPORTED, None, None
    #     else:
    #         last_update = self._get_data_last_update(tags)
    #         if last_update is None or last_update < today():
    #             need_update = DataUtility.RESULT_TRUE
    #         else:
    #             need_update = DataUtility.RESULT_FALSE
    #         return need_update, None, None

    def _check_dict_param(self, argv: dict, param_info: dict, must_params: list = None) -> bool:
        nop(self)
        if argv is None or len(argv) == 0:
            return False
        keys = list(argv.keys())
        for param in param_info.keys():
            if param not in keys:
                if must_params is None or param in must_params:
                    logger.info('Param key check error: Param is missing - ' + param)
                    return False
                else:
                    continue

            value = argv[param]
            types, values = param_info[param]
            if value is None and None in types:
                continue
            if not isinstance(value, tuple([t for t in types if t is not None])):
                logger.info('Param key check error: Param type mismatch - ' +
                            str(type(value)) + ' is not in ' + str(types))
                return False

            if len(values) > 0:
                if value not in values:
                    logger.info('Param key check error: Param value out of range - ' +
                                str(value) + ' is not in ' + str(values))
                    return False
        return True

    def _check_dataframe_field(self, df: pd.DataFrame, field_info: dict, must_fields: list = None) -> bool:
        """
        Check whether DataFrame filed fits the field info.
        :param df: The DataFrame you want to check
        :param field_info: The definition of fields info
        :param must_fields: The must fields.
                            If not None, the specified fields must exist.
                            If None, all fields should exist.
        :return: True if all fields are satisfied. False if not.
        """
        nop(self)
        if df is None or len(df) == 0:
            return False
        columns = list(df.columns)
        for field in field_info.keys():
            if field not in columns:
                if must_fields is None or field in must_fields:
                    logger.info('DataFrame field check error: Field is missing - ' + field)
                    return False
                else:
                    continue

            type_ok = False
            type_df = df[field].dtype
            types, values = field_info[field]
            for py_type in types:
                df_type = PYTHON_DATAFRAME_TYPE_MAPPING.get(py_type)
                if df_type is not None and df_type == type_df:
                    type_ok = True
                    break
            if not type_ok:
                logger.info('DataFrame field check error: Field type mismatch - ' +
                            str(type_df) + ' is not in ' + str(types))
                return False

            if len(values) > 0:
                out_of_range_values = df[~df[field].isin(values)]
                if len(out_of_range_values) > 0:
                    logger.info('DataFrame field check error: Field value out of range - ' +
                                str(out_of_range_values) + ' is not in ' + str(values))
                    return False
        return True

    def __normalize_tags(self, tags: list) -> tuple:
        _tags = tags if isinstance(tags, list) else [tags]
        while len(_tags) < 3:
            _tags.append('')
        return tuple(_tags)
















