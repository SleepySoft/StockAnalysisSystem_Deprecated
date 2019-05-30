import sys
import json
import traceback
from datetime import datetime

import config
import pymongo
from pymongo import MongoClient


def text2date(text: str) -> datetime:
    return datetime.strptime(text, '%Y-%m-%d')


def text2datetime(text: str) -> datetime:
    return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')


def text_auto_time(text: str) -> datetime:
    # noinspection PyBroadException
    try:
        return datetime.strptime(text, '%Y-%m-%d')
    except Exception:
        pass
    # noinspection PyBroadException
    try:
        return datetime.strptime(text, '%H:%M:%S')
    except Exception:
        pass
    # noinspection PyBroadException
    try:
        return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
    except Exception:
        pass
    return None


def date2text(time: datetime) -> str:
    return time.strftime('%Y-%m-%d')


def datetime2text(time: datetime) -> str:
    return time.strftime('%Y-%m-%d %H:%M:%S')


'''
Itkv = Identity, DateTime, Key, Value
This table is based on NoSQL (MongoDB)
It must contain an Identity and a Timestamp as unique index
Other Key-Value pairs are extendable
'''


class ItkvTable:
    def __init__(self, client: MongoClient, database: str, table: str):
        self.__client = client
        self.__database = database
        self.__table = table

    def upsert(self, identity: str, time: datetime or str, data: dict, extra_spec: dict = None) -> dict:
        # Update a record, insert if not exists.
        # identity and time are also the conditions to find the entries
        collection = self.__get_collection()
        if collection is None:
            return False
        spec = self.__gen_find_spec(identity, time, time, extra_spec)
        if isinstance(time, str):
            time = text_auto_time(time)
        document = {
            'Identity': identity,
            'DateTime': datetime2text(time),
            **data
        }
        return collection.update(spec, document, True)

    def delete(self, identity: str or list, since: datetime = None, until: datetime = None,
               extra_spec: dict = None, keys: list = None):
        # Update a record, insert if not exists.
        # keys - The keys you want to remove, None to move the whole entry
        collection = self.__get_collection()
        if collection is None:
            return False
        spec = self.__gen_find_spec(identity, since, until, extra_spec)

        if keys is None:
            return collection.delete_many(spec)
        else:
            del_keys = {}
            for key in keys:
                del_keys[key] = 1
            return collection.update(spec, {'$unset': del_keys}, False, True)

    # Query records
    # keys - The keys you want to list in your query, None to list all
    def query(self, identity: str or list, since: datetime = None, until: datetime = None,
              extra_spec: dict = None, keys: list = None) -> list:
        collection = self.__get_collection()
        if collection is None:
            return False
        spec = self.__gen_find_spec(identity, since, until, extra_spec)

        key_select = None
        if keys is not None:
            key_select = {}
            for key in keys:
                key_select[key] = 1

        return list(collection.find(spec, key_select))

    # ------------------------------------------------------------------------------------------------------------------

    def __get_collection(self):
        if self.__client is None:
            return None
        db = self.__client[self.__database]
        if db is None:
            return None
        collection = db[self.__table]
        return collection

    def __gen_find_spec(self, identity: str or list,
                        since: datetime or str = None,
                        until: datetime or str = None,
                        extra_spec: dict = None) -> dict:
        # Generate find spec for NoSQL query.
        # Parameters
        #   @identity - str or list of str, None if you don't want to specify
        #   @since, until - datetime or time format str, None if you don't want to specify
        #   @extra_spec - dict, to specify the extra conditions, None if you don't want to specify
        # Return value: The spec dict

        if identity is None:
            spec = {}
        elif isinstance(identity, str):
            spec = {'Identity': identity}
        elif isinstance(identity, list):
            spec = {'Identity': {'$in': identity}}
        else:
            raise Exception('<identity> should be str or a list of str, or just None')

        if isinstance(since, str):
            since = text_auto_time(since)
        elif isinstance(since, datetime) or since is None:
            pass
        else:
            raise Exception('<since> should be time format str or datetime, or just None')

        if isinstance(until, str):
            until = text_auto_time(since)
        elif isinstance(until, datetime) or until is None:
            pass
        else:
            raise Exception('<until> should be time format str or datetime, or just None')

        time_limit = {}
        if since is not None:
            time_limit['$gte'] = datetime2text(since)
        if until is not None:
            time_limit['$lte'] = datetime2text(until)
        if len(time_limit) > 0:
            spec['DateTime'] = time_limit

        if extra_spec is not None and len(extra_spec) > 0:
            spec.update(extra_spec)

        return spec


# ----------------------------------------------------- Test Code ------------------------------------------------------

def __value_should_be(identity: str, since: datetime, until: datetime):
    pass


def __document_count(identity: str, since: datetime, until: datetime):
    pass


def test_basic_feature():
    client = MongoClient(config.DB_HOST, config.DB_PORT, serverSelectionTimeoutMS=5)
    assert(client is not None)

    table = ItkvTable(client, 'TestDatabase', 'TestTable')

    table.upsert('identity1', '2000-05-01', {
        'PI': 3.1415926,
        'Speed of Light': 299792458,
        'Password': "Who's your daddy",
        "Schindler's List": ['Trump', 'Bili', 'Anonymous']
    })
    table.upsert('identity2', '2020-03-01', {
        'A1': 111,
        'B1': 222,
        'C1': 333,
        "D1": 444
    })

    result = table.query('identity1')
    assert(len(result) == 1)
    collection = result[0]
    assert(collection['PI'] == 3.1415926)
    assert(collection['Speed of Light'] == 299792458)
    assert(collection['Password'] == "Who's your daddy")
    assert(collection["Schindler's List"] == ['Trump', 'Bili', 'Anonymous'])


# ----------------------------------------------------- File Entry -----------------------------------------------------

def main():
    test_basic_feature()


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

