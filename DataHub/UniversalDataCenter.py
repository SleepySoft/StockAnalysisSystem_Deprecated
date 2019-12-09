import sys
import datetime
import traceback
import pandas as pd

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


UPDATE_STRATEGY_TYPE = int

UPDATE_STRATEGY_AUTO = 1
UPDATE_STRATEGY_POSITIVE = 2
UPDATE_STRATEGY_MANUAL = 3
UPDATE_STRATEGY_OFFLINE = 4


class UniversalDataTable:
    def __init__(self, uri: str, identify_field: str, time_serial_field: str):
        self.__uri = uri
        self.__identify_field = identify_field
        self.__time_serial_field = time_serial_field

        self.__table = None

    # -------------------------------------------------------------------

    def adapt(self, uri: str) -> bool:
        return self.__uri == uri

    def query(self, uri: str, identify: str or [str], time_serial: tuple, extra: dict) -> pd.DataFrame or None:
        pass

    def merge(self, df: pd.DataFrame):
        pass

    def range(self, uri: str, identify: str) -> (datetime.datetime, datetime.datetime) or None:
        nop(uri)
        nop(identify)
        return None

    def ref_range(self, uri: str, identify: str) -> (datetime.datetime, datetime.datetime) or None:
        nop(uri)
        nop(identify)
        return None

    def update_range(self) -> (datetime.datetime, datetime.datetime) or None:
        pass

    def depot_name(self, uri: str, identify: str or [str], time_serial: tuple, extra: dict) -> str:
        nop(self)
        nop(identify)
        nop(time_serial)
        nop(extra)
        return uri.replace('.', '_')


# ----------------------------------------------------------------------------------------------------------------------

class UniversalDataCenter:

    def __init__(self, plugin: PluginManager, update: UpdateTableEx):
        self.__plugin_manager = plugin
        self.__update_table = update
        self.__last_error = ''
        self.__data_table = []

    def get_plugin_manager(self) -> PluginManager:
        return self.__plugin_manager

    def get_update_table(self) -> UpdateTableEx:
        return self.__update_table

    def get_data_table(self, uri: str) -> UniversalDataTable:
        for table in self.__data_table:
            if table.adapt(uri):
                return table
        return None

    def get_last_error(self) -> str:
        return self.__last_error

    def log_error(self, error_text: str):
        self.__last_error = error_text

    # -------------------------------------------------------------------

    def query(self, uri: str, identify: str or [str], time_serial: tuple, extra: dict) -> pd.DataFrame or None:
        return self.query_from_local(uri, identify, time_serial, extra)

    def query_from_local(self, uri: str, identify: str or [str],
                         time_serial: tuple, extra: dict) -> pd.DataFrame or None:
        table = self.get_data_table(uri)
        if table is None:
            self.log_error('Cannot find data table for : ' + uri)
        result = table.query(uri, identify, time_serial, extra)
        return result

    def query_from_plugin(self, uri: str, identify: str or [str],
                          time_serial: tuple, extra: dict) -> pd.DataFrame or None:
        argv = {
                'identify':         identify,
                'time_serial':      time_serial,
            }.update(extra if isinstance(extra, dict) else {})

        plugins = self.get_plugin_manager().find_module_has_capacity(uri)
        for plugin in plugins:
            df = self.get_plugin_manager().execute_module_function(plugin, 'query', uri, argv)
            if df is not None and isinstance(df, pd.DataFrame) and len(df) > 0:
                return df
        return None

    def update_local_data(self, uri: str, identify: str or [str], time_serial: tuple, extra: dict) -> bool:
        table = self.get_data_table(uri)
        if table is None:
            self.log_error('Cannot find data table for : ' + uri)
            return False

        local_data_range = table.range(uri, identify)
        last_udpate = self.get_update_table().get_last_update_time(identify.split('.'))

        result = self.query_from_plugin(uri, identify, time_serial, extra)
        if result is None:
            self.log_error('Cannot fetch data from plugin for : ' + uri)
            return False


