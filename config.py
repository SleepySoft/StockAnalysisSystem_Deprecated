import json
import traceback

# NOSQL_DB_HOST = 'localhost'
# NOSQL_DB_PORT = 27017
# NOSQL_DB_USER = ''
# NOSQL_DB_PASS = ''


# How to get a tushare pro token:
#   Register an account with this link (my referral link): https://tushare.pro/register?reg=271027
#   Check your token (official document): https://tushare.pro/document/1?doc_id=39
#   How to earn your score (official document): https://tushare.pro/document/1?doc_id=13
TS_TOKEN = 'TODO: Place holder, for compatibility.'


class Config:
    MUST_CONFIG = ['NOSQL_DB_HOST', 'NOSQL_DB_PORT', 'TS_TOKEN']

    def __init__(self):
        self.__config_dict = {}

    def set(self, key: str, value: str):
        self.__config_dict[key] = value

    def get(self, key: str, default_value: str = '') -> str:
        return self.__config_dict.get(key, default_value)

    def save_config(self, config_file: str = 'config.json') -> bool:
        try:
            with open(config_file, 'wt') as f:
                json.dump(self.__config_dict, f)
            return True
        except Exception as e:
            print('Save config fail.')
            print(e)
            print(traceback.format_exc())
            return False
        finally:
            pass

    def load_config(self, config_file: str = 'config.json'):
        try:
            with open(config_file, 'rt') as f:
                self.__config_dict = json.load(f)
            if self.__config_dict is None or len(self.__config_dict) == 0:
                self.__config_dict = {}
                return False
            return True
        except Exception as e:
            print('Load config fail.')
            print(e)
            print(traceback.format_exc())
            return False
        finally:
            pass

    def check_config(self) -> (bool, str):
        success, reason = True, []
        for must_config in Config.MUST_CONFIG:
            if self.get(must_config) == '':
                success = False
                reason.append('必要设置: ' + must_config + '为空')
        return success, '\n'.join(reason)

