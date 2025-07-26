from flask import Flask, render_template, request, jsonify
from datetime import datetime
import calendar

import db
import date_util
import enums
from enums import State

app = Flask(__name__)

year_days = []
year = -1
now = datetime.now()
active_dates = set()
day_data = []

@app.get('/')
def index():
    global year_days
    global year
    global now
    global active_dates
    global tasks
    global day_data
    
    now = datetime.now()
    year_days = date_util.get_year_days(now.year)
    year = now.year
    active_dates = set(db.get_active_dates(now.year))
    day_data = db.get_day(date_util.dt_to_str(now))

    return render_template(
        'index.html',
        year_days=year_days,
        year=year,
        now=now,
        active_dates=active_dates,
        day_data=day_data,

        dt_to_str=date_util.dt_to_str,
        month_name=calendar.month_name,
        format_num=date_util.format_num,
        State=enums.State
    )

@app.post('/state/<int:task_id>')
def update_state(task_id: int):
    state_id = int(request.args.get('state_id') or -1)
    record_id = int(request.args.get('record_id') or -1)
    if state_id == State.DONE:
        db._execute(f"INSERT INTO records (task_id, state_id) VALUES ({task_id}, {State.DONE})")
        record_id = db._execute("SELECT MAX(record_id) FROM records")
        return [ State.DONE, record_id ]
    elif state_id == State.PASS:
        db._execute(f"UPDATE records SET state_id={State.PASS} WHERE record_id={record_id}")
        return [ State.PASS ]
    else:
        db._execute(f"DELETE FROM records WHERE record_id={record_id}")
        return [  ]

@app.get('/now')
def get_now():
    global now
    now = datetime.now()
    return now

@app.get('/year-days/<int:year>')
def get_year_days(_year: int):
    global year
    global year_days
    year = _year
    year_days = date_util.get_year_days(_year)
    return year_days

@app.post('/task/<string:task>')
def add_task(task: str):
    try:
        global day_data
        global now
        db.add_task(task)
        day_data = get_day_data(date_util.dt_to_str(now))
        return render_template('tasks.html', day_data=day_data, State=enums.State)
    except Exception as e:
        print('ERROR:', e)
        return []
    
@app.delete('/task/<string:task_ids>')
def delete_task(task_ids: str):
    try:
        global day_data
        global now
        db.delete_task(task_ids)
        day_data = get_day_data(date_util.dt_to_str(now))
        print(day_data)
        return render_template('tasks.html', day_data=day_data, State=enums.State)

    except Exception as e:
        print('ERROR:', e)
        return [500]

@app.get('/calendar')
def get_calendar():
    return render_template(
        'calendar.html',
        year_days=date_util.get_year_days(now.year),
        active_dates=db.get_active_dates(now.year),
        month_name=calendar.month_name,
        format_num=date_util.format_num,
        dt_to_str=date_util.dt_to_str,
        now=now,
        year=year
    )

@app.get('/active-dates')
def get_active_dates():
    global active_dates
    global year
    active_dates = db.get_active_dates(year)
    return active_dates

@app.get('/day-data/<string:dt>')
def get_day_data(dt: str):
    global day_data
    day_data = db.get_day(dt)
    return day_data

if __name__ == '__main__':
    app.run(debug=True)