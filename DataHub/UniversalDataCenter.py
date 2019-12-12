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
    from Database import NoSqlRw
    from Database import UpdateTableEx
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Database import NoSqlRw
    from Database import UpdateTableEx
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
finally:
    logger = logging.getLogger('')


# UPDATE_STRATEGY_TYPE = int
#
# UPDATE_STRATEGY_AUTO = 1
# UPDATE_STRATEGY_POSITIVE = 2
# UPDATE_STRATEGY_MANUAL = 3
# UPDATE_STRATEGY_OFFLINE = 4


class UniversalDataTable:
    def __init__(self, uri: str, depot_name: str, table_prefix: str,
                 identity_field: str = 'Identity', datetime_field: str = 'DateTime'):
        self.__uri = uri
        self.__depot_name = depot_name
        self.__table_prefix = table_prefix
        self.__identity_field = identity_field
        self.__datetime_field = datetime_field

    # -------------------------------------------------------------------

    def adapt(self, uri: str) -> bool:
        return self.__uri == uri

    def query(self, uri: str, identify: str or [str], time_serial: tuple, extra: dict) -> pd.DataFrame or None:
        pass

    def merge(self, uri: str, identify: str, df: pd.DataFrame):
        table = self.data_table(uri, identify, (None, None), {})
        identity_field, datetime_field = table.identity_field(), table.datetime_field()

        for index, row in df.iterrows():
            if NoSqlRw.str_available(identity_field):
                identity_value = row[identity_field]
            else:
                identity_value = None
            if NoSqlRw.str_available(datetime_field):
                datetime_value = row[datetime_field]
                if isinstance(datetime_value, str):
                    datetime_value = text_auto_time(datetime_value)
            else:
                datetime_value = None
            table.upsert(identity_value, datetime_value, row.to_dict())

    def range(self, uri: str, identify: str) -> (datetime.datetime, datetime.datetime) or None:
        table = self.data_table(uri, identify, (None, None), {})
        return table.min_of(table.datetime_field()), table.max_of(table.datetime_field())

    def ref_range(self, uri: str, identify: str) -> (datetime.datetime, datetime.datetime) or None:
        pass

    def update_range(self) -> (datetime.datetime, datetime.datetime) or None:
        pass

    def data_table(self, uri: str, identify: str or [str], time_serial: tuple, extra: dict) -> NoSqlRw.ItkvTable:
        nop(identify, time_serial, extra)
        return DatabaseEntry().query_nosql_table(self.__depot_name, uri.replace('.', '_'),
                                                 self.__identity_field, self.__datetime_field)


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


