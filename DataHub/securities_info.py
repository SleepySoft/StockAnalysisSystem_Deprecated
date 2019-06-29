import traceback
import pandas as pd

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    from DataHub.DataUtility import DataUtility
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Utiltity.plugin_manager import PluginManager
    from Database.Database import Database
    from Database.DataTable import DataTable
    from Database.UpdateTable import UpdateTable
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    from DataHub.DataUtility import DataUtility
    from Utiltity.common import *
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Utiltity.plugin_manager import PluginManager
    from Database.Database import Database
    from Database.DataTable import DataTable
    from Database.UpdateTable import UpdateTable
    from Utiltity.plugin_manager import PluginManager
finally:
    pass


NEED_COLLECTOR_CAPACITY = [
    'SecuritiesInfo',
]
SECURITIES_EXCHANGE = ['SSE', 'SZSE']
TABLE_SECURITIES_INFO = 'SecuritiesInfo'
IDENTITY_SECURITIES_INFO = '<stock_code>.<exchange>'
FIELD_INFO = {'code':           (['str'], []),
              'name':           (['str'], []),
              'area':           (['str'], []),
              'industry':       (['str'], []),
              'fullname':       (['str'], []),
              'en_name':        (['str'], []),
              'market':         (['str'], []),
              'exchange':       (['str'], ['SSE', 'SZSE']),
              'currency':       (['str'], []),
              'list_status':    (['int'], []),
              'listing_date':   (['datetime'], []),
              'delisting_date': (['datetime'], []),
              'stock_connect':  (['int'], [])
              }


class SecuritiesInfo:
    def __init__(self):
        pass








