from datetime import datetime


def now() -> datetime:
    return datetime.now()


def today() -> datetime:
    date_text = datetime.today().strftime('%Y-%m-%d')
    return text2date(date_text)


def tomorrow() -> datetime:
    date_text = (datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return text2date(date_text)


def yesterday() -> datetime:
    date_text = (datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return text2date(date_text)


def text_auto_time(text: str) -> datetime:
    if isinstance(text, datetime):
        return text
    # noinspection PyBroadException
    try:
        return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
    except Exception:
        pass
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
        return datetime.strptime(text, '%Y%m%d')
    except Exception:
        pass
    return None


def text2date(text: str) -> datetime:
    return datetime.strptime(text, '%Y-%m-%d')


def text2datetime(text: str) -> datetime:
    return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')


def date2text(time: datetime) -> str:
    return time.strftime('%Y-%m-%d')


def datetime2text(time: datetime) -> str:
    return time.strftime('%Y-%m-%d %H:%M:%S')

