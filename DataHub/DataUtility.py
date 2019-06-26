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
    from Database.Database import Database
    from Database import UpdateTable
    from Database.DataTable import DataTable
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Database.Database import Database
    from Database import UpdateTable
    from Database.DataTable import DataTable
    from Utiltity.plugin_manager import PluginManager
finally:
    pass


class DataUtility:

    RESULT_CODE = object
    RESULT_FALSE = False
    RESULT_TRUE = True
    RESULT_SUCCESSFUL = 2
    RESULT_FAILED = 4
    RESULT_NOT_SUPPORTED = 8
    RESULT_NOT_IMPLEMENTED = None

    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, plugin: PluginManager, update: UpdateTable):
        self.__plugin = plugin
        self.__update = update

    def get_update_table(self) -> UpdateTable:
        return self.__update

    def get_plugin_manager(self) -> PluginManager:
        return self.__plugin

    # --------------------------------------------------- public if ---------------------------------------------------

    def query_data(self, tags: [str],
                   timeval: (datetime.datetime, datetime.datetime) = None,
                   extra: dict = None) -> pd.DataFrame:
        if self.need_update(tags) == DataUtility.RESULT_TRUE:
            self.execute_update(tags)
        return self.data_from_cache(tags, timeval, extra)

    def need_update(self, tags: [str]) -> (RESULT_CODE, datetime, datetime):
        """
        Check whether the tag specified data need update.
        It will check data range first. If reference data range is not specified.
            The 'update_since' and 'update_until' are always None
            It will check the last update instead.
        If reference last update is also not specified.
            The 'need_update' will be RESULT_NOT_SUPPORTED
            The 'update_since' and 'update_until' are always None if the last update checking is applied.
        :param tags: The tags to identify the data
        :return: Tuple: (
            need_update :   RESULT_TRUE if need update,
                            RESULT_FALSE if don't need update,
                            RESULT_NOT_SUPPORTED if not not support update check,
            update_since : The data we need update since.
            update_until : The data we need update until.
            )
        """

        need_update, update_since, update_until = self._check_update_by_range(tags)
        if need_update == DataUtility.RESULT_NOT_SUPPORTED:
            need_update, update_since, update_until = self._check_update_by_last_update(tags)
        return need_update, update_since, update_until

    def execute_update(self, tags: [str]) -> RESULT_CODE:
        return DataUtility.RESULT_NOT_IMPLEMENTED

    # --------------------------------------------------- private if ---------------------------------------------------

    def data_from_cache(self, tags: [str],
                        timeval: (datetime.datetime, datetime.datetime),
                        extra: dict = None) -> pd.DataFrame:
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
        return [datetime.datetime(1990, 1, 1), yesterday()]

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

    def _check_update_by_range(self, tags: [str]) -> (RESULT_CODE, datetime, datetime):
        ref_since, ref_until = self.get_reference_data_range(tags)
        if ref_since is None and ref_until is None:
            return DataUtility.RESULT_NOT_SUPPORTED, None, None

        need_update = DataUtility.RESULT_FALSE
        update_since, update_until = None, None
        since, until = self.get_cached_data_range(tags)

        if ref_since is not None:
            if since is None or since > ref_since:
                update_since = ref_since
                need_update = DataUtility.RESULT_TRUE
            else:
                update_since = tomorrow_of(until)
        if ref_until is not None:
            if until is None or until < ref_until:
                update_until = ref_until
                need_update = DataUtility.RESULT_TRUE
            else:
                update_until = yesterday_of(ref_since)
        return need_update, update_since, update_until

    def _check_update_by_last_update(self, tags: [str]) -> (RESULT_CODE, datetime, datetime):
        reference_last_update = self.get_reference_last_update(tags)
        if reference_last_update is None:
            return DataUtility.RESULT_NOT_SUPPORTED, None, None
        else:
            need_update = DataUtility.RESULT_TRUE if reference_last_update != today() else DataUtility.RESULT_FALSE
            return need_update, None, None

    def __normalize_tags(self, tags: list) -> tuple:
        _tags = tags if isinstance(tags, list) else [tags]
        while len(_tags) < 3:
            _tags.append('')
        return tuple(_tags)
















