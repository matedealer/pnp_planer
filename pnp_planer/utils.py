from datetime import datetime, timedelta
import calendar
import locale
from config import TIME_FORMATER, DEFAULT_STARTTIME

KEY_WORDS = {'today':['heute','today','now'],
             'tomorrow':['morgen','tomorrow'],
             }

locale.setlocale(locale.LC_ALL, 'de_DE')
WOCHENTAGE = [day.lower() for day in calendar.day_name]
WOCHENTAGE_ABK = [day.lower() for day in calendar.day_abbr]

locale.setlocale(locale.LC_ALL, 'C')
WEEKDAYS = [day.lower() for day in calendar.day_name]
WEEKDAYS_ABBR = [day.lower() for day in calendar.day_abbr]


def string_to_date(date):
    weekday = None
    ret = None
    set_default_time = True

    if date.lower() in KEY_WORDS['today']:
        ret =  datetime.today()
    if date.lower() in KEY_WORDS['tomorrow']:
        ret = datetime.today() + timedelta(days=1)

    if date.lower() in WOCHENTAGE:
        weekday = WOCHENTAGE.index(date.lower())
    if date.lower() in WOCHENTAGE_ABK:
        weekday = WOCHENTAGE_ABK.index(date.lower())
    if date.lower() in WEEKDAYS:
        weekday = WEEKDAYS.index(date.lower())
    if date.lower() in WEEKDAYS_ABBR:
        weekday = WEEKDAYS_ABBR.index(date.lower())

    if weekday:
        delta = datetime.today().weekday() - weekday
        if delta < 0:
            delta = weekday - datetime.today().weekday()
        if delta == 0:
            delta = 7

        ret = datetime.today() + timedelta(days=delta)

    try:
        ret =  datetime.strptime(date, '%d.%m.%Y-%H:%M')
        set_default_time = False
    except ValueError:
        pass

    try:
        ret =  datetime.strptime(date, '%d.%m.%Y')
    except ValueError:
        pass

    try:
        ret =  datetime.strptime("{}.{}".format(date, datetime.now().strftime("%Y")), '%d.%m.%Y')
    except ValueError:
        pass


    if ret and ret > datetime.now() - timedelta(days=1):
        if set_default_time:
            ret = ret.replace(**DEFAULT_STARTTIME)
        return ret

    return None

