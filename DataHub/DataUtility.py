import logging

import numpy as np
import pandas as pd
from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import Utiltity.common as common
    from Utiltity.time_utility import *
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
    from DataHub.UniversalDataCenter import ParameterChecker
    from DataHub.UniversalDataCenter import UniversalDataTable
    from DataHub.UniversalDataCenter import UniversalDataCenter
except Exception as e:
    sys.path.append(root_path)

    import Utiltity.common as common
    from Utiltity.time_utility import *
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
    from DataHub.UniversalDataCenter import ParameterChecker
    from DataHub.UniversalDataCenter import UniversalDataTable
    from DataHub.UniversalDataCenter import UniversalDataCenter
finally:
    logger = logging.getLogger('')


def csv_name_column_to_identity(csv_file: str, column: str) -> bool:
    df = pd.read_csv(csv_file, index_col=None)
    if column not in list(df.columns):
        return False
    from stock_analysis_system import StockAnalysisSystem
    data_utility = StockAnalysisSystem().get_data_hub_entry().get_data_utility()
    name_column = df[column].values.tolist()
    id_column = data_utility.names_to_stock_identity(name_column)
    df[column] = np.array(id_column)
    df.to_csv(csv_file + '_parsed.csv')


class DataUtility:
    def __init__(self, data_center: UniversalDataCenter):
        self.__data_center = data_center

        self.__stock_id_information_table = {}
        self.__stock_history_name_id_table = {}

    def refresh_securities_cache(self):
        securities_info = self.__data_center.query('Market.SecuritiesInfo',
                                                   fields=['stock_identity', 'name', 'listing_date'])
        if securities_info is not None:
            self.__stock_id_information_table = {row['stock_identity']: (row['name'], row['listing_date'])
                                                 for index, row in securities_info.iterrows()}

        securities_used_name = self.__data_center.query('Market.NamingHistory',
                                                        fields=['stock_identity', 'name', 'naming_date'])
        if securities_used_name is not None:
            self.__stock_history_name_id_table = {
                # Convert to lower case and remove * mark for easy indexing.
                row['name'].lower().replace('*', ''): (row['stock_identity'],
                                                       row['naming_date'])
                for index, row in securities_used_name.iterrows()}
            
            # Also add current name into history naming list
            if securities_info is not None:
                for key, info in self.__stock_id_information_table.items():
                    trimed_name = info[0].lower().replace('*', '')
                    if trimed_name not in self.__stock_history_name_id_table.keys():
                        self.__stock_history_name_id_table[trimed_name] = (key, today())

    def get_stock_list(self) -> [(str, str)]:
        if len(self.__stock_id_information_table) == 0:
            self.refresh_securities_cache()
        return [(_id, _info[0]) for _id, _info in self.__stock_id_information_table.items()]
        # result = self.__data_center.query('Market.SecuritiesInfo', fields=['stock_identity', 'name'])
        # return [(line.get('stock_identity', ''), line.get('name', '')) for line in result]

    def get_stock_identities(self) -> [str]:
        if len(self.__stock_id_information_table) == 0:
            self.refresh_securities_cache()
        return [_id for _id, _info in self.__stock_id_information_table.items()]

    def names_to_stock_identity(self, names: [str]) -> [str]:
        if len(self.__stock_id_information_table) == 0:
            self.refresh_securities_cache()
        if not isinstance(names, list):
            names = [str(names)]
        # The result is a tuple like (stock_identity, naming_date)
        # We'll keep the original name if there's no match record.
        # Too simple: [self.__stock_history_name_id_table.get(name, (name, ''))[0] for name in names]

        ids = []
        for name in names:
            _id = self.__stock_history_name_id_table.get(name.lower(), ('', ''))[0]
            if _id != '':
                ids.append(_id)
            else:
                # For debug
                ids.append(name)
        return ids

        # stock_list = self.get_stock_list()
        # name_id_table = {stock_name: stock_id for stock_id, stock_name in stock_list}
        #
        # ids = []
        # for name in names:
        #     name = name_id_table.get(name, name)
        #     identity = common.normalize_stock_identity(name)
        #     ids.append(identity if identity != '' else name)
        # return ids

    def get_stock_listing_date(self, stock_identity: str, default_val: datetime.datetime) -> datetime.datetime:
        return self.__stock_id_information_table[stock_identity][1] \
            if stock_identity in self.__stock_id_information_table.keys() else default_val























