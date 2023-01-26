import datetime
import time

from enacrestic import const


def utc_to_local(utc_dt):
    """
    convert UTC datetime to local timezone datetime
    """
    epoch = time.mktime(utc_dt.timetuple())
    offset = datetime.datetime.fromtimestamp(
        epoch
    ) - datetime.datetime.utcfromtimestamp(epoch)
    return utc_dt + offset


def utc_to_local_str(utc_dt):
    """
    convert UTC datetime to local timezone datetime in string
    """
    return datetime.datetime.strftime(utc_to_local(utc_dt), const.DATE_FORMAT)


def local_to_utc(dt):
    """
    convert local timezone datetime to UTC datetime
    """
    epoch = time.mktime(dt.timetuple())
    offset = datetime.datetime.fromtimestamp(
        epoch
    ) - datetime.datetime.utcfromtimestamp(epoch)
    return dt - offset


def local_str_to_utc(dt):
    """
    convert local timezone datetime in string to UTC datetime
    """
    return local_to_utc(datetime.datetime.strptime(dt, const.DATE_FORMAT))
