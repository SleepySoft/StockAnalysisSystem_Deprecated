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

    def need_update(self, tags: [str]) -> RESULT_CODE:
        return DataUtility.RESULT_NOT_IMPLEMENTED

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
        nop(self, tags)
        return None, None

    def get_cache_last_update(self, tags: [str]) -> datetime.datetime:
        nop(self, tags)
        return None

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

    def __normalize_tags(self, tags: list) -> tuple:
        _tags = tags if isinstance(tags, list) else [tags]
        while len(_tags) < 3:
            _tags.append('')
        return tuple(_tags)
















