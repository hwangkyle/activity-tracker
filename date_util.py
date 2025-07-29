from datetime import datetime
from calendar import monthrange
from typing import List

import db

def get_year_days(year: int):
    return [_get_month_days(year, month) for month in range(1, 13)]

def _get_month_days(year: int, month: int) -> List[List[int | None]]:
    first_weekday, num_days = monthrange(year, month)
    first_weekday = (first_weekday + 1) % 7

    day_count = 1
    days = []
    while day_count <= num_days:
        week = []
        for _ in range(7):
            if first_weekday != 0 or day_count > num_days:
                week.append(None)
                first_weekday -= 1
                continue
            date = f'{year}-{format_num(month)}-{format_num(day_count)}'
            week.append((day_count, db.get_num_done(date)))
            day_count += 1
        days.append(week)
    
    return days

def format_num(num: int|str) -> str:
    if num >= 10:
        return str(num)
    return f'0{num}'

def dt_to_str(dt: datetime) -> str:
    return f'{dt.year}-{format_num(dt.month)}-{format_num(dt.day)} {format_num(dt.hour)}:{format_num(dt.minute)}:{format_num(dt.second)}'