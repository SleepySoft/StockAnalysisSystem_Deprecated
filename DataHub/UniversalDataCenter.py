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


class ParameterChecker:

    PYTHON_DATAFRAME_TYPE_MAPPING = {
        'str': 'object',
        'int64': 'int',
        'datetime': 'datetime64[ns]',
    }

    # Key: str - The key you need to check in the dict param
    # Val: tuple - The first item: The list of expect types for this key, you can specify a None if None is allowed
    #              The second item: The list of expect values for this key, an empty list means it can be any value
    DICT_PARAM_INFO_EXAMPLE = {
        'identify':     ([str], ['id1', 'id2']),
        'datetime':     ([datetime.datetime, None], [])
    }

    # The param info for checking a dataframe.
    # It's almost likely to the dict param info except the type should be str instead of real python type
    DATAFRAME_PARAM_INFO_EXAMPLE = {
        'identity':         (['str'], []),
        'period':           (['datetime'], [])}                # The last day of report period

    def __init__(self,
                 df_param_info: dict = None, df_must_params: list = None,
                 dict_param_info: dict = None, dict_must_params: list = None):
        self.__df_param_info = df_param_info
        self.__df_must_params = df_must_params
        self.__dict_param_info = dict_param_info
        self.__dict_must_params = dict_must_params

    def check_dict(self, argv: dict) -> bool:
        if self.__dict_param_info is None or len(self.__dict_param_info) == 0:
            return True
        return ParameterChecker.check_dict_param(argv, self.__dict_param_info, self.__dict_must_params)

    def check_dataframe(self, df: dict) -> bool:
        if self.__df_param_info is None or len(self.__df_param_info) == 0:
            return True
        return ParameterChecker.check_dict_param(df, self.__df_param_info, self.__df_must_params)

    @staticmethod
    def check_dict_param(argv: dict, param_info: dict, must_params: list = None) -> bool:
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

    @staticmethod
    def check_dataframe_field(df: pd.DataFrame, field_info: dict, must_fields: list = None) -> bool:
        """
        Check whether DataFrame filed fits the field info.
        :param df: The DataFrame you want to check
        :param field_info: The definition of fields info
        :param must_fields: The must fields.
                            If not None, the specified fields must exist.
                            If None, all fields should exist.
        :return: True if all fields are satisfied. False if not.
        """
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
                df_type = ParameterChecker.PYTHON_DATAFRAME_TYPE_MAPPING.get(py_type)
                if df_type is not None and df_type == type_df:
                    type_ok = True
                    break
            if not type_ok:
                logger.info('DataFrame field check error: Field type mismatch - ' +
                            str(df_type) + ' is not in ' + str(df_type))
                return False

            if len(values) > 0:
                out_of_range_values = df[~df[field].isin(values)]
                if len(out_of_range_values) > 0:
                    logger.info('DataFrame field check error: Field value out of range - ' +
                                str(out_of_range_values) + ' is not in ' + str(values))
                    return False
        return True


class UniversalDataTable:
    def __init__(self, uri: str, database_entry: DatabaseEntry, depot_name: str,
                 table_prefix: str, identity_field: str = 'Identity', datetime_field: str = 'DateTime'):
        self.__uri = uri.lower()
        self.__database_entry = database_entry
        self.__depot_name = depot_name
        self.__table_prefix = table_prefix
        self.__identity_field = identity_field
        self.__datetime_field = datetime_field

    def identity_field(self) -> str or None:
        return self.__identity_field

    def datetime_field(self) -> str or None:
        return self.__datetime_field

    # -------------------------------------------------------------------

    def adapt(self, uri: str) -> bool:
        return self.__uri == uri

    def query(self, uri: str, identify: str or [str], time_serial: tuple,
              extra: dict, fields: list) -> pd.DataFrame or None:
        table = self.data_table(uri, identify, time_serial, extra)
        since = time_serial[0] if time_serial is not None and \
                                  isinstance(time_serial, (list, tuple)) and len(time_serial) > 0 else None
        until = time_serial[1] if time_serial is not None and \
                                  isinstance(time_serial, (list, tuple)) and len(time_serial) > 1 else None
        result = table.query(identify, since, until, extra, fields)
        return result

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

    def range(self, uri: str, identify: str) -> (datetime.datetime, datetime.datetime):
        table = self.data_table(uri, identify, (None, None), {})
        return table.min_of(table.datetime_field()), table.max_of(table.datetime_field())

    def ref_range(self, uri: str, identify: str) -> (datetime.datetime, datetime.datetime):
        nop(self, uri, identify)
        return None, None

    def update_range(self, uri: str, identify: str) -> (datetime.datetime, datetime.datetime):
        local_since, local_until = self.range(uri, identify)
        ref_since, ref_until = self.ref_range(uri, identify)
        return local_until, ref_until

    def data_table(self, uri: str, identify: str or [str], time_serial: tuple, extra: dict) -> NoSqlRw.ItkvTable:
        nop(identify, time_serial, extra)
        return self.__database_entry.query_nosql_table(self.__depot_name, uri.replace('.', '_'),
                                                       self.__identity_field, self.__datetime_field)


# ----------------------------------------------------------------------------------------------------------------------

class UniversalDataCenter:

    def __init__(self, database_entry: DatabaseEntry, collector_plugin: PluginManager):
        self.__database_entry = database_entry
        self.__plugin_manager = collector_plugin
        self.__last_error = ''
        self.__data_table = []

    def get_plugin_manager(self) -> PluginManager:
        return self.__plugin_manager

    def get_update_table(self) -> UpdateTableEx:
        return self.__database_entry.get_update_table()

    def get_data_table(self, uri: str) -> UniversalDataTable:
        for table in self.__data_table:
            if table.adapt(uri):
                return table
        return None

    def get_last_error(self) -> str:
        return self.__last_error

    def log_error(self, error_text: str):
        self.__last_error = error_text

    def register_data_table(self, table: UniversalDataTable):
        if table not in self.__data_table:
            self.__data_table.append(table)

    # -------------------------------------------------------------------

    def query(self, uri: str, identify: str or [str], time_serial: tuple, extra: dict) -> pd.DataFrame or None:
        return self.query_from_local(uri, identify, time_serial, extra)

    def query_from_local(self, uri: str, identify: str or [str],
                         time_serial: tuple, extra: dict) -> pd.DataFrame or None:
        table = self.get_data_table(uri)
        if table is None:
            self.log_error('Cannot find data table for : ' + uri)
            return None
        result = table.query(uri, identify, time_serial, extra)
        return result

    def query_from_plugin(self, uri: str, identify: str or [str],
                          time_serial: tuple, extra: dict = None) -> pd.DataFrame or None:
        table = self.get_data_table(uri)

        if table is not None:
            identity_field = table.identity_field()
            datetime_field = table.datetime_field()
        else:
            identity_field = None
            datetime_field = None
        if not NoSqlRw.str_available(identity_field):
            identity_field = 'identify'
        if not NoSqlRw.str_available(datetime_field):
            datetime_field = 'datetime'

        argv = {
            'uri':          uri,
            identity_field: identify,
            datetime_field: time_serial,
        }
        argv.update(extra if isinstance(extra, dict) else {})

        plugins = self.get_plugin_manager().find_module_has_capacity(uri)
        for plugin in plugins:
            df = self.get_plugin_manager().execute_module_function(plugin, 'query', argv)
            if df is not None and isinstance(df, pd.DataFrame) and len(df) > 0:
                return df
        return None

    def update_local_data(self, uri: str, identify: str or [str],
                          time_serial: tuple = None, extra: dict = None) -> bool:
        table = self.get_data_table(uri)
        if table is None:
            self.log_error('Cannot find data table for : ' + uri)
            return False

        since, until = normalize_time_serial(time_serial, None, None)
        if since is not None and until is not None:
            # User specified
            pass
        else:
            # Guess the update date time range
            update_since, update_until = table.update_range()
            if update_since is not None and update_until is not None:
                # Auto detect successfully
                since, until = update_since, update_until
            else:
                last_update = self.get_update_table().get_last_update_time(identify.split('.'))
                since = last_update
                until = today()

        if since == until:
            # Does not need update.
            return True

        result = self.query_from_plugin(uri, identify, (min(since, until), max(since, until)), extra)
        if result is None:
            self.log_error('Cannot fetch data from plugin for : ' + uri)
            return False

        table.merge(uri, identify, result)
        self.get_update_table().update_latest_update_time(identify.split('.'))

        return True


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Test --------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def __build_data_center() -> UniversalDataCenter:
    plugin_path = root_path + '/Collector/'

    collector_plugin = PluginManager(plugin_path)
    collector_plugin.refresh()

    return UniversalDataCenter(DatabaseEntry(), collector_plugin)


def test_entry1():
    data_center = __build_data_center()
    df = data_center.query_from_plugin('test.entry1', 'identify_test1', ('2030-02-01', '2030-04-01'))
    print(df)
    assert len(df) == 28 + 30 + 1
    assert bool(set(list(df.columns)).intersection(['datetime', 'field_01', 'field_02', 'field_03', 'identify_test1']))


def test_update():
    data_center = __build_data_center()
    data_center.register_data_table(
        UniversalDataTable('test.entry1', DatabaseEntry(), 'test_db', 'test_table'))
    data_center.update_local_data('test.entry1', 'identify_test1')


def test_entry():
    # test_entry1()
    test_update()


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


if __name__ == "__main__":
    sys.excepthook = exception_hook
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass

