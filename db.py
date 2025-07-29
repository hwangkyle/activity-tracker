import sqlite3 as sql
from typing import Any, List, Tuple
from datetime import datetime, timezone

from enums import State

DB_PATH = '' # Path to db here

def _get_offset() -> int:
    """
    In minutes (add to UTC to get local)
    """
    local_dt = datetime.now()

    _utc_dt = datetime.now(timezone.utc)
    utc_dt = datetime(
        _utc_dt.year,
        _utc_dt.month,
        _utc_dt.day,
        _utc_dt.hour,
        _utc_dt.minute,
        _utc_dt.second,
        _utc_dt.microsecond
    )

    diff_dt = local_dt - utc_dt

    return int(diff_dt.total_seconds() / 60)

def _execute(query: str) -> List[Any]:
    conn = sql.connect(DB_PATH)

    cursor = conn.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    
    conn.commit()
    conn.close()

    return rows


def get_tasks() -> List[Any]:
    return _execute("SELECT task_id, task FROM tasks")

def get_active_dates(year: int, task_ids: str | None = None) -> List[Any]:
    """
    Only gets this year.
    """
    task_ids_where = '' if task_ids is None else f' AND task_id IN ({task_ids})'
    rows = _execute(
        f"""
        SELECT DISTINCT date(r.datetime, '{_get_offset()} minute') as date
        FROM records r
        WHERE date >= '{year}' AND state_id=1{task_ids_where}
        """
    )
    results = list(map(lambda x: x[0], rows))

    return results

def get_day(dt: str) -> List[Any]:
    """
    dt should be in local time.
    """
    sql = f"""SELECT t.task_id, task, r.record_id, s.state_id, s.state, datetime
        FROM tasks t
        LEFT JOIN records r ON t.task_id=r.task_id AND date('{dt}')=date(r.datetime, '{_get_offset()} minute')
        LEFT JOIN states s ON r.state_id=s.state_id
        """
    print(sql)
    return _execute(sql)

def add_task(task: str) -> None:
    _execute(f"INSERT INTO tasks (task) VALUES ('{task}')")

def delete_task(task_ids: str) -> None:
    _execute(f"DELETE FROM records WHERE task_id IN ({task_ids})")
    _execute(f"DELETE FROM tasks WHERE task_id IN ({task_ids})")

def change_task_name(task_id: int, task_name: str) -> None:
    _execute(f"UPDATE tasks SET task='{task_name}' WHERE task_id={task_id}")

def get_num_done(dt: str) -> Tuple[int, int]:
    sql = f"""SELECT count(record_id), count(*)
        FROM tasks t
        LEFT JOIN records r ON t.task_id=r.task_id AND date('{dt}')=date(r.datetime, '{_get_offset()} minute')
        """
    print(sql)
    results = _execute(sql)
    return results[0]