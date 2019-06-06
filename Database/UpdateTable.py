import sys
import traceback
from datetime import datetime

try:
    from Database.Database import Database
except Exception as e:
    from os import sys, path
    root = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(root)
    from Database.Database import Database
finally:
    pass


class UpdateTable:
    TABLE = 'UpdateTable'
    FIELD = ['Serial', 'L1Tag', 'L2Tag', 'L3Tag', 'LastUpdate']

    def __init__(self):
        pass

    def today(self) -> datetime:
        today_text = self.today_text()
        today = datetime.strptime(today_text, '%Y-%m-%d')
        return today

    def today_text(self) -> str:
        return datetime.today().strftime('%Y-%m-%d')

    def today_updated(self, tag1: str, tag2: str, tag3: str):
        return self.get_latest_update_time(tag1, tag2, tag3) == self.today()

    def renew_update_time(self, tag1: str, tag2: str, tag3: str):
        sql_update = ("UPDATE %s SET LastUpdate = '%s' WHERE L1Tag='%s' AND L2Tag='%s' AND L3Tag='%s';" %
                      (UpdateTable.TABLE, self.today_text(), tag1, tag2, tag3))

        sql_insert = ("INSERT INTO %s (L1Tag, L2Tag, L3Tag, LastUpdate) VALUES ('%s', '%s', '%s', '%s');" %
                      (UpdateTable.TABLE, tag1, tag2, tag3, self.today_text()))

        if self.get_latest_update_time(tag1, tag2, tag3) is None:
            return Database().get_utility_db().QuickExecuteDML(sql_insert, True)
        else:
            return Database().get_utility_db().QuickExecuteDML(sql_update, True)

    def delete_update_record(self, tag1: str, tag2: str, tag3: str):
        sql_delete = ("DELETE FROM %s WHERE  L1Tag='%s' AND L2Tag='%s' AND L3Tag='%s';" %
                      (UpdateTable.TABLE, tag1, tag2, tag3))
        return Database().get_utility_db().QuickExecuteDML(sql_delete, True)

    def get_latest_update_time(self, tag1: str, tag2: str, tag3: str) -> datetime:
        result = self.get_latest_update_time_record(tag1, tag2, tag3)
        if len(result) == 0:
            return None
        else:
            date_text = result[0][4]
            date = datetime.strptime(date_text, '%Y-%m-%d')
            return date

    def get_latest_update_time_record(self, tag1: str, tag2: str, tag3: str) -> []:
        return Database().get_utility_db().ListFromDB(
            UpdateTable.TABLE, UpdateTable.FIELD, "L1Tag = '%s' AND L2Tag = '%s' AND L3Tag = '%s'" % (tag1, tag2, tag3))


# ----------------------------------------------------- Test Code ------------------------------------------------------


def __clear_test_entry(ut: UpdateTable):
    ut.delete_update_record('__Finance Data', 'Annual', '000001')
    ut.delete_update_record('__Finance Data', 'Annual', '000005')
    ut.delete_update_record('__Index Component', '123456', '')
    ut.delete_update_record('__Index Component', '567890', '')
    ut.delete_update_record('__Trade Calender', '', '')
    ut.delete_update_record('__Trade News', '', '')


def test_basic_feature():
    ut = UpdateTable()

    assert(ut.renew_update_time('__Finance Data', 'Annual', '000001'))
    assert(ut.renew_update_time('__Finance Data', 'Annual', '000005'))
    assert(ut.renew_update_time('__Index Component', '123456', ''))
    assert(ut.renew_update_time('__Index Component', '567890', ''))
    assert(ut.renew_update_time('__Trade Calender', '', ''))
    assert(ut.renew_update_time('__Trade News', '', ''))

    assert(ut.get_latest_update_time('__Finance Data', 'Annual', '000001') == ut.today())
    assert(ut.get_latest_update_time('__Finance Data', 'Annual', '000005') == ut.today())
    assert(ut.get_latest_update_time('__Index Component', '123456', '') == ut.today())
    assert(ut.get_latest_update_time('__Index Component', '567890', '') == ut.today())
    assert(ut.get_latest_update_time('__Trade Calender', '', '') == ut.today())
    assert(ut.get_latest_update_time('__Trade News', '', '') == ut.today())

    ut.delete_update_record('__Finance Data', 'Annual', '000001')
    ut.delete_update_record('__Finance Data', 'Annual', '000005')
    ut.delete_update_record('__Index Component', '123456', '')
    ut.delete_update_record('__Index Component', '567890', '')
    ut.delete_update_record('__Trade Calender', '', '')
    ut.delete_update_record('__Trade News', '', '')

    assert(ut.get_latest_update_time('__Finance Data', 'Annual', '000001') is None)
    assert(ut.get_latest_update_time('__Finance Data', 'Annual', '000005') is None)
    assert(ut.get_latest_update_time('__Index Component', '123456', '') is None)
    assert(ut.get_latest_update_time('__Index Component', '567890', '') is None)
    assert(ut.get_latest_update_time('__Trade Calender', '', '') is None)
    assert(ut.get_latest_update_time('__Trade News', '', '') is None)

    __clear_test_entry(ut)


def test_record_unique():
    ut = UpdateTable()

    assert(ut.renew_update_time('__Finance Data', 'Annual', '000001'))
    assert(ut.renew_update_time('__Finance Data', 'Annual', '000001'))
    assert(ut.renew_update_time('__Finance Data', 'Annual', '000001'))

    assert(ut.renew_update_time('__Index Component', '123456', ''))
    assert(ut.renew_update_time('__Index Component', '123456', ''))
    assert(ut.renew_update_time('__Index Component', '123456', ''))

    assert(ut.renew_update_time('__Trade Calender', '', ''))
    assert(ut.renew_update_time('__Trade Calender', '', ''))
    assert(ut.renew_update_time('__Trade Calender', '', ''))

    assert(len(ut.get_latest_update_time_record('__Finance Data', 'Annual', '000001')) == 1)
    assert(len(ut.get_latest_update_time_record('__Index Component', '123456', '')) == 1)
    assert(len(ut.get_latest_update_time_record('__Trade Calender', '', '')) == 1)

    __clear_test_entry(ut)


def test_entry():
    test_basic_feature()
    test_record_unique()


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










