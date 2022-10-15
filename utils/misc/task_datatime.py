import datetime


def to_datatime(data: str):
    return datetime.datetime.strptime(data, "%Y-%m-%d %H:%M")


def split_on_week(date: datetime.datetime)->tuple:
    from datetime import datetime, timedelta
    import calendar
    year = date.year
    month = date.month
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1

    list_left, list_right = [], []

    start, end = datetime(year = date.year, month= date.month, day=1), (datetime(year = year, month= month, day=1)+ timedelta(days = -1))
    if start == end:
        print(1)
        print(start.strftime('%Y-%m-%d') + ' ' + end.strftime('%Y-%m-%d'))
    else:
        while True:
            after = start

            while after.isoweekday() != 7:
                after += timedelta(days=1)

            if after < end:
                list_left.append(start)
                list_right.append(after+timedelta(days=1))
                start = after
                start += timedelta(days=1)
            else:
                list_left.append(start)
                list_right.append(end+timedelta(days=1))
                break

        result = (list_left, list_right)
        print(len(result))
        print(result)
        return result


def data_checker(data: str):
    try:
        dt = datetime.datetime.strptime(data, "%Y-%m-%d %H:%M")
    except:
        return "некоректний формат даних!"

    now = datetime.datetime.now(tz=None)
    plus_20m = datetime.timedelta(minutes=20)
    now_plus_20m = now + plus_20m

    if dt < now:
        return "ви намагажєтесь запланувати на минуле"
    elif dt < now_plus_20m:
        return "годі вам, це буде швидше як за 20 хвилин, ми вам не потрібні"

    return False

