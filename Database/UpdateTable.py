import sys
import traceback
from datetime import datetime
from Database import Database

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    from Utiltity.time_utility import *
except Exception as e:
    sys.path.append(root_path)

    from Utiltity.time_utility import *
finally:
    pass


class UpdateTable:
    TABLE = 'UpdateTable'
    FIELD = ['Serial', 'L1Tag', 'L2Tag', 'L3Tag', 'Since', 'Until', 'LastUpdate']

    def __init__(self):
        pass

    def today_text(self) -> str:
        return datetime.today().strftime('%Y-%m-%d')

    def get_since(self, tag1: str, tag2: str, tag3: str):
        record = self.get_update_record(tag1, tag2, tag3)
        return None if len(record) == 0 else text_auto_time(record[0][4])

    def get_until(self, tag1: str, tag2: str, tag3: str):
        record = self.get_update_record(tag1, tag2, tag3)
        return None if len(record) == 0 else text_auto_time(record[0][5])

    def update_since(self, tag1: str, tag2: str, tag3: str, since: datetime or str):
        sql_update = ("UPDATE %s SET Since = '%s' WHERE L1Tag='%s' AND L2Tag='%s' AND L3Tag='%s';" %
                      (UpdateTable.TABLE, text_auto_time(since), tag1, tag2, tag3))
        sql_insert = ("INSERT INTO %s (L1Tag, L2Tag, L3Tag, Since, LastUpdate) VALUES ('%s', '%s', '%s', '%s', '%s');" %
                      (UpdateTable.TABLE, tag1, tag2, tag3, text_auto_time(since), self.today_text()))

        record = self.get_update_record(tag1, tag2, tag3)
        if record is None or len(record) == 0:
            return Database().get_utility_db().QuickExecuteDML(sql_insert, True)
        elif record[0][4] is None or text_auto_time(since) < text_auto_time(record[0][4]):
            return Database().get_utility_db().QuickExecuteDML(sql_update, True)
        else:
            return True

    def update_until(self, tag1: str, tag2: str, tag3: str, until: datetime or str):
        sql_update = ("UPDATE %s SET Until = '%s', LastUpdate = '%s' WHERE L1Tag='%s' AND L2Tag='%s' AND L3Tag='%s';" %
                      (UpdateTable.TABLE, text_auto_time(until), self.today_text(), tag1, tag2, tag3))
        sql_insert = ("INSERT INTO %s (L1Tag, L2Tag, L3Tag, Until, LastUpdate) VALUES ('%s', '%s', '%s', '%s', '%s');" %
                      (UpdateTable.TABLE, tag1, tag2, tag3, text_auto_time(until), self.today_text()))

        record = self.get_update_record(tag1, tag2, tag3)
        if record is None or len(record) == 0:
            return Database().get_utility_db().QuickExecuteDML(sql_insert, True)
        elif record[0][5] is None or text_auto_time(until) > text_auto_time(record[0][5]):
            return Database().get_utility_db().QuickExecuteDML(sql_update, True)
        else:
            return True

    # def renew_update_time(self, tag1: str, tag2: str, tag3: str):
    #     sql_update = ("UPDATE %s SET LastUpdate = '%s' WHERE L1Tag='%s' AND L2Tag='%s' AND L3Tag='%s';" %
    #                   (UpdateTable.TABLE, self.today_text(), tag1, tag2, tag3))
    #
    #     sql_insert = ("INSERT INTO %s (L1Tag, L2Tag, L3Tag, LastUpdate) VALUES ('%s', '%s', '%s', '%s');" %
    #                   (UpdateTable.TABLE, tag1, tag2, tag3, self.today_text()))
    #
    #     if self.get_latest_update_time(tag1, tag2, tag3) is None:
    #         return Database().get_utility_db().QuickExecuteDML(sql_insert, True)
    #     else:
    #         return Database().get_utility_db().QuickExecuteDML(sql_update, True)

    def get_update_record(self, tag1: str, tag2: str, tag3: str) -> []:
        return Database().get_utility_db().ListFromDB(
            UpdateTable.TABLE, UpdateTable.FIELD, "L1Tag = '%s' AND L2Tag = '%s' AND L3Tag = '%s'" % (tag1, tag2, tag3))

    def delete_update_record(self, tag1: str, tag2: str, tag3: str):
        sql_delete = ("DELETE FROM %s WHERE  L1Tag='%s' AND L2Tag='%s' AND L3Tag='%s';" %
                      (UpdateTable.TABLE, tag1, tag2, tag3))
        return Database().get_utility_db().QuickExecuteDML(sql_delete, True)

    # def get_latest_update_time(self, tag1: str, tag2: str, tag3: str) -> datetime:
    #     result = self.get_latest_update_time_record(tag1, tag2, tag3)
    #     if len(result) == 0:
    #         return None
    #     else:
    #         date_text = result[0][4]
    #         date = datetime.strptime(date_text, '%Y-%m-%d')
    #         return date


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
    __clear_test_entry(ut)

    assert(ut.update_since('__Finance Data', 'Annual', '000001', '19900101'))
    assert(ut.update_until('__Finance Data', 'Annual', '000001', '20200101'))

    assert(ut.update_since('__Finance Data', 'Annual', '000005', '19910202'))
    assert(ut.update_until('__Finance Data', 'Annual', '000005', '20210202'))

    assert(ut.update_since('__Index Component', '123456', '', '19920303'))
    assert(ut.update_until('__Index Component', '123456', '', '20220303'))

    assert(ut.update_since('__Index Component', '567890', '', '19930404'))
    assert(ut.update_until('__Index Component', '567890', '', '20230404'))

    assert(ut.update_since('__Trade Calender', '', '', '19940505'))
    assert(ut.update_until('__Trade Calender', '', '', '20240505'))

    assert(ut.update_since('__Trade News', '', '', '19950606'))
    assert(ut.update_until('__Trade News', '', '', '20250606'))

    # --------------------------------------------------------------------------

    assert(ut.get_since('__Finance Data', 'Annual', '000001') == text_auto_time('19900101'))
    assert(ut.get_until('__Finance Data', 'Annual', '000001') == text_auto_time('20200101'))

    assert(ut.get_since('__Finance Data', 'Annual', '000005') == text_auto_time('19910202'))
    assert(ut.get_until('__Finance Data', 'Annual', '000005') == text_auto_time('20210202'))

    assert(ut.get_since('__Index Component', '123456', '') == text_auto_time('19920303'))
    assert(ut.get_until('__Index Component', '123456', '') == text_auto_time('20220303'))

    assert(ut.get_since('__Index Component', '567890', '') == text_auto_time('19930404'))
    assert(ut.get_until('__Index Component', '567890', '') == text_auto_time('20230404'))

    assert(ut.get_since('__Trade Calender', '', '') == text_auto_time('19940505'))
    assert(ut.get_until('__Trade Calender', '', '') == text_auto_time('20240505'))

    assert(ut.get_since('__Trade News', '', '') == text_auto_time('19950606'))
    assert(ut.get_until('__Trade News', '', '') == text_auto_time('20250606'))

    # --------------------------------------------------------------------------

    ut.delete_update_record('__Finance Data', 'Annual', '000001')
    ut.delete_update_record('__Finance Data', 'Annual', '000005')
    ut.delete_update_record('__Index Component', '123456', '')
    ut.delete_update_record('__Index Component', '567890', '')
    ut.delete_update_record('__Trade Calender', '', '')
    ut.delete_update_record('__Trade News', '', '')

    assert(ut.get_since('__Finance Data', 'Annual', '000001') is None)
    assert(ut.get_until('__Finance Data', 'Annual', '000001') is None)

    assert(ut.get_since('__Finance Data', 'Annual', '000005') is None)
    assert(ut.get_until('__Finance Data', 'Annual', '000005') is None)

    assert(ut.get_since('__Index Component', '123456', '') is None)
    assert(ut.get_until('__Index Component', '123456', '') is None)

    assert(ut.get_since('__Index Component', '567890', '') is None)
    assert(ut.get_until('__Index Component', '567890', '') is None)

    assert(ut.get_since('__Trade Calender', '', '') is None)
    assert(ut.get_until('__Trade Calender', '', '') is None)

    assert(ut.get_since('__Trade News', '', '') is None)
    assert(ut.get_until('__Trade News', '', '') is None)

    __clear_test_entry(ut)


def test_since_record_unique_and_decrease():
    ut = UpdateTable()
    __clear_test_entry(ut)

    assert(ut.update_since('__Finance Data', 'Annual', '000001', '20200101'))
    assert(ut.update_since('__Finance Data', 'Annual', '000001', '20000102'))
    assert(ut.update_since('__Finance Data', 'Annual', '000001', '20100103'))

    assert(ut.update_since('__Index Component', '123456', '', '20200101'))
    assert(ut.update_since('__Index Component', '123456', '', '20100101'))
    assert(ut.update_since('__Index Component', '123456', '', '20150101'))

    assert(ut.update_since('__Trade Calender', '', '', '20300101'))
    assert(ut.update_since('__Trade Calender', '', '', '19000101'))
    assert(ut.update_since('__Trade Calender', '', '', '19910101'))

    assert(len(ut.get_update_record('__Finance Data', 'Annual', '000001')) == 1)
    assert(len(ut.get_update_record('__Index Component', '123456', '')) == 1)
    assert(len(ut.get_update_record('__Trade Calender', '', '')) == 1)

    assert(ut.get_since('__Finance Data', 'Annual', '000001') == text_auto_time('20000102'))
    assert(ut.get_since('__Index Component', '123456', '') == text_auto_time('20100101'))
    assert(ut.get_since('__Trade Calender', '', '') == text_auto_time('19000101'))

    __clear_test_entry(ut)


def test_until_record_unique_and_increase():
    ut = UpdateTable()
    __clear_test_entry(ut)

    assert(ut.update_until('__Finance Data', 'Annual', '000001', '20200101'))
    assert(ut.update_until('__Finance Data', 'Annual', '000001', '20200102'))
    assert(ut.update_until('__Finance Data', 'Annual', '000001', '20100103'))

    assert(ut.update_until('__Index Component', '123456', '', '20200101'))
    assert(ut.update_until('__Index Component', '123456', '', '20210101'))
    assert(ut.update_until('__Index Component', '123456', '', '20120101'))

    assert(ut.update_until('__Trade Calender', '', '', '20300101'))
    assert(ut.update_until('__Trade Calender', '', '', '20400101'))
    assert(ut.update_until('__Trade Calender', '', '', '20200101'))

    assert(len(ut.get_update_record('__Finance Data', 'Annual', '000001')) == 1)
    assert(len(ut.get_update_record('__Index Component', '123456', '')) == 1)
    assert(len(ut.get_update_record('__Trade Calender', '', '')) == 1)

    assert(ut.get_until('__Finance Data', 'Annual', '000001') == text_auto_time('20200102'))
    assert(ut.get_until('__Index Component', '123456', '') == text_auto_time('20210101'))
    assert(ut.get_until('__Trade Calender', '', '') == text_auto_time('20400101'))

    __clear_test_entry(ut)


def test_entry():
    test_basic_feature()
    test_since_record_unique_and_decrease()
    test_until_record_unique_and_increase()


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










