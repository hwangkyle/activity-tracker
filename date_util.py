from datetime import datetime
from calendar import monthrange
from typing import List

def get_year_days(year: int):
    return [get_month_days(year, month) for month in range(1, 13)]

def get_month_days(year: int, month: int) -> List[List[int | None]]:
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
            week.append(day_count)
            day_count += 1
        days.append(week)
    
    return days

def format_num(num: int) -> str:
    if num >= 10:
        return str(num)
    return f'0{num}'