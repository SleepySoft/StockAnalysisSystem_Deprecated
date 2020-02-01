import datetime
import time


def now() -> datetime.datetime:
    return datetime.datetime.now()


def today() -> datetime.datetime:
    date_text = datetime.datetime.today().strftime('%Y-%m-%d')
    return text2date(date_text)


def tomorrow() -> datetime.datetime:
    date_text = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return text2date(date_text)


def yesterday() -> datetime.datetime:
    date_text = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return text2date(date_text)


def days_ago(days: int) -> datetime.datetime:
    now_date = datetime.datetime.today()
    now_date -= datetime.timedelta(days=days)
    date_text = now_date.strftime('%Y-%m-%d')
    return text2date(date_text)


def years_ago(years: int) -> datetime.datetime:
    now_date = datetime.datetime.today()
    now_date -= datetime.timedelta(days=years*365)
    date_text = now_date.strftime('%Y-%m-%d')
    return text2date(date_text)


def tomorrow_of(time: datetime.datetime):
    return time + datetime.timedelta(days=1)


def yesterday_of(time: datetime.datetime):
    return time - datetime.timedelta(days=1)


def text_auto_time(text: str) -> datetime.datetime:
    if isinstance(text, datetime.datetime):
        return text
    # noinspection PyBroadException
    try:
        return datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
    except Exception:
        pass
    # noinspection PyBroadException
    try:
        return datetime.datetime.strptime(text, '%Y-%m-%d')
    except Exception:
        pass
    # noinspection PyBroadException
    try:
        return datetime.datetime.strptime(text, '%H:%M:%S')
    except Exception:
        pass
    # noinspection PyBroadException
    try:
        return datetime.datetime.strptime(text, '%Y%m%d')
    except Exception:
        pass
    return None


def text2date(text: str) -> datetime.datetime:
    return datetime.datetime.strptime(text, '%Y-%m-%d')


def text2datetime(text: str) -> datetime.datetime:
    return datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S')


def date2text(time: datetime.datetime) -> str:
    return time.strftime('%Y-%m-%d')


def datetime2text(time: datetime.datetime) -> str:
    return time.strftime('%Y-%m-%d %H:%M:%S')


def default_since() -> datetime.datetime:
    return text2date('1900-01-01')


def normalize_time_serial(time_serial: tuple or list,
                          since_default: datetime.datetime = None,
                          until_default: datetime.datetime = None) -> (datetime.datetime, datetime.datetime):
    since = time_serial[0] if time_serial is not None and \
                              isinstance(time_serial, (list, tuple)) and len(time_serial) > 0 else since_default
    until = time_serial[1] if time_serial is not None and \
                              isinstance(time_serial, (list, tuple)) and len(time_serial) > 1 else until_default
    if since is not None and not isinstance(since, datetime.datetime):
        since = text_auto_time(str(since))
    if until is not None and not isinstance(until, datetime.datetime):
        until = text_auto_time(str(until))
    return since, until


# ----------------------------------------------------------------------------------------------------------------------

class Clock:
    def __init__(self):
        self.__start = time.time()

    def reset(self):
        self.__start = time.time()

    def elapsed(self) -> float:
        return time.time() - self.__start

    def elapsed_s(self) -> int:
        return int(time.time() - self.__start)

    def elapsed_ms(self) -> int:
        return int((time.time() - self.__start) * 1000)


# ----------------------------------------------------------------------------------------------------------------------

class Delayer:
    def __init__(self, delay_ms: int):
        self.__delay = delay_ms
        self.__clock = Clock()

    def reset(self):
        self.__clock.reset()

    def delay(self):
        elapsed = self.__clock.elapsed()
        if elapsed < self.__delay / 1000:
            time.sleep(self.__delay / 1000 - elapsed)


