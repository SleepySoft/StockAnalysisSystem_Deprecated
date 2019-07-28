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


class ItkvTable:
    """ A table which can easily extend its column, with identity and time as its main key.
    Itkv = Identity, DateTime, Key, Value
    This table is based on NoSQL (MongoDB)
    It must contain an Identity and a Timestamp as unique index
    Other Key-Value pairs are extendable
    """

    def __init__(self, client: MongoClient, database: str, table: str):
        self.__client = client
        self.__database = database
        self.__table = table

    def drop(self):
        collection = self.__get_collection()
        if collection is None:
            return True
        collection.drop()

    def count(self) -> int:
        collection = self.__get_collection()
        if collection is None:
            return 0
        return collection.count()

    def upsert(self, identity: str, time: datetime or str, data: dict, extra_spec: dict = None) -> dict:
        """ Update a record, insert if not exists.
        Args:
            identity    : str or list of str, None if you don't want to specify
            time        : datetime or time format str, None if you don't want to specify
            extra_spec  : dict, to specify the extra conditions, None if you don't want to specify
            identity and time are also the conditions to find the entries
        Return value:
            The result of API returns, as dict
        Raises:
            None
        """

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
        return collection.update(spec, {'$set': document}, True)

    def delete(self, identity: str or list = None, since: datetime = None, until: datetime = None,
               extra_spec: dict = None, keys: list = None):
        """ Delete document or delete key-value in document.
        Args:
            identity        : str or list of str, None if you don't want to specify
            since, until    : datetime or time format str, None if you don't want to specify
            extra_spec      : dict, to specify the extra conditions, None if you don't want to specify
            keys            : The keys you want to remove, None to move the whole document
        Return value:
            The result of API returns, as dict
        Raises:
            None
        """

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
            return collection.update(spec, {'$unset': del_keys}, False, True, True)

    # Query records
    # keys - The keys you want to list in your query, None to list all
    def query(self, identity: str or list = None, since: datetime = None, until: datetime = None,
              extra_spec: dict = None, keys: list = None) -> list:
        """ Query records
        Args:
            identity        : str or list of str, None if you don't want to specify
            since, until    : datetime or time format str, None if you don't want to specify
            extra_spec      : dict, to specify the extra conditions, None if you don't want to specify
            keys            : The keys you want to query, None to query all entries
        Return value:
            Result as dict list
        Raises:
            None
        """

        collection = self.__get_collection()
        if collection is None:
            return []
        spec = self.__gen_find_spec(identity, since, until, extra_spec)

        key_select = None
        if keys is not None:
            key_select = {}
            for key in keys:
                key_select[key] = 1
        result = collection.find(spec, key_select)
        return list(result)

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
        """ Generate find spec for NoSQL query.
        Args:
            identity        : str or list of str, None if you don't want to specify
            since, until    : datetime or time format str, None if you don't want to specify
            extra_spec      : dict, to specify the extra conditions, None if you don't want to specify
        Return value:
            The spec dict
        Raises:
            None
        """

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
            until = text_auto_time(until)
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

def __prepare_default_test_data() -> ItkvTable:
    client = MongoClient(config.NOSQL_DB_HOST, config.NOSQL__DB_PORT, serverSelectionTimeoutMS=5)
    assert(client is not None)

    table = ItkvTable(client, 'TestDatabase', 'TestTable')
    table.drop()
    table.upsert('identity1', '2000-05-01', {
        'PI': 3.1415926,
        'Speed of Light': 299792458,
        'Password': "Who's your daddy",
        "Schindler's List": ['Trump', 'Bili', 'Anonymous'],
        'Author': 'Sleepy',
    })
    table.upsert('identity2', '2020-03-01', {
        'A1': 111,
        'B1': 222,
        'C1': 333,
        "D1": 444,
        'Author': 'Sleepy',
    })
    return table


def test_basic_update_query_drop():
    table = __prepare_default_test_data()

    result = table.query('identity1')
    assert(len(result) == 1)
    document = result[0]
    assert(document['PI'] == 3.1415926)
    assert(document['Speed of Light'] == 299792458)
    assert(document['Password'] == "Who's your daddy")
    assert(document["Schindler's List"] == ['Trump', 'Bili', 'Anonymous'])

    table.drop()

    result = table.query('identity1')
    assert(len(result) == 0)


def test_query():
    table = __prepare_default_test_data()

    # Test since option

    result = table.query(since='2010-01-01')
    assert(len(result) == 1)

    result = table.query(since='2020-03-01')
    assert(len(result) == 1)

    result = table.query(since='2020-03-01 00:00:01')
    assert(len(result) == 0)

    result = table.query(since='2000-05-01')
    assert(len(result) == 2)

    # Test until option

    result = table.query(until='2010-01-01')
    assert(len(result) == 1)

    result = table.query(until='2000-05-01')
    assert(len(result) == 1)

    result = table.query(until='2000-04-30 23:59:29')
    assert(len(result) == 0)

    result = table.query(until='2030-01-01')
    assert(len(result) == 2)

    # Test extra_spec

    result = table.query(extra_spec={'A1': 111})
    assert(len(result) == 1)

    result = table.query(extra_spec={'PI': 3.14})
    assert(len(result) == 0)

    result = table.query(extra_spec={'Author': 'Sleepy'})
    assert(len(result) == 2)


def test_delete_document():
    table = __prepare_default_test_data()
    assert(len(table.query()) == 2)
    table.delete('identity1')
    assert(len(table.query()) == 1)

    table = __prepare_default_test_data()
    assert(len(table.query()) == 2)
    table.delete(since='2015-01-01')
    assert(len(table.query()) == 1)

    table = __prepare_default_test_data()
    assert(len(table.query()) == 2)
    table.delete(since='2000-01-01')
    assert(len(table.query()) == 0)

    table = __prepare_default_test_data()
    assert(len(table.query()) == 2)
    table.delete(until='2019-09-01')
    assert(len(table.query()) == 1)

    table = __prepare_default_test_data()
    assert(len(table.query()) == 2)
    table.delete(until='2020-09-01')
    assert(len(table.query()) == 0)

    table = __prepare_default_test_data()
    assert(len(table.query()) == 2)
    table.delete(extra_spec={'A1': 111})
    assert(len(table.query()) == 1)

    table = __prepare_default_test_data()
    assert(len(table.query()) == 2)
    table.delete(extra_spec={'Author': 'Sleepy'})
    assert(len(table.query()) == 0)


def test_delete_key_value():
    table = __prepare_default_test_data()
    assert(len(table.query()) == 2)

    table.delete(keys=['PI', 'A1', 'Author'])
    collection = table.query()

    assert(len(collection) == 2)
    for document in collection:
        assert('PI' not in document.keys())
        assert('A1' not in document.keys())
        assert('Author' not in document.keys())


def test_update_key_value():
    table = __prepare_default_test_data()
    assert(len(table.query()) == 2)

    table.upsert('identity1', data={
        'PI': 3.14,
        'Password': "Greed is good",
        'New': 'New Item',
    })

    table.upsert('identity3', '2015-06-06', data={
        'D1': 555,
        'Password': "Greed is good",
        'New': 'New Item',
    })

    table.upsert('identity1', '2000-05-01', {
        'PI': 3.1415926,
        'Speed of Light': 299792458,
        'Password': "Who's your daddy",
        "Schindler's List": ['Trump', 'Bili', 'Anonymous'],
        'Author': 'Sleepy',
    })
    table.upsert('identity2', '2020-03-01', {
        'A1': 111,
        'B1': 222,
        'C1': 333,
        "D1": 444,
        'Author': 'Sleepy',
    })


def test_entry():
    test_basic_update_query_drop()
    test_query()
    test_delete_document()
    test_delete_key_value()


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

