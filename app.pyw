from flask import Flask, render_template, request, jsonify
from datetime import datetime
import calendar
import darkdetect

import db
import date_util
import enums
from enums import State

app = Flask(__name__)

year_days = []
year = -1
now = datetime.now()
display_date = date_util.dt_to_str(now)
day_data = []

dark_mode = darkdetect.isDark()

@app.get('/')
def index():
    global year_days
    global year
    global now
    global display_date
    global tasks
    global day_data
    
    now = datetime.now()
    display_date = date_util.dt_to_str(now)
    year_days = date_util.get_year_days(now.year)
    year = now.year
    day_data = db.get_day(display_date)

    return render_template(
        'index.html',
        year_days=year_days,
        year=year,
        now=now,
        day_data=day_data,

        dt_to_str=date_util.dt_to_str,
        month_name=calendar.month_name,
        format_num=date_util.format_num,
        State=enums.State,

        dark_mode=dark_mode,
        bottom_text=db.get_bottom_text()
    )

@app.post('/state/<int:task_id>/<int:curr_ms>')
def update_state(task_id: int, curr_ms: int):
    state_id = int(request.args.get('state_id') or -1)
    record_id = int(request.args.get('record_id') or -1)
    if state_id == State.DONE:
        x = f"INSERT INTO records (task_id, state_id, datetime) VALUES ({task_id}, {State.DONE}, datetime({curr_ms} / 1000, 'unixepoch'))"
        db._execute(x)
        record_id = db._execute("SELECT MAX(record_id) FROM records")
        return [ State.DONE, record_id ]
    elif state_id == State.PASS:
        x = f"UPDATE records SET state_id={State.PASS} WHERE record_id={record_id}"
        db._execute(x)
        return [ State.PASS ]
    else:
        db._execute(f"DELETE FROM records WHERE record_id={record_id}")
        return [  ]

@app.post('/task/<string:task>')
def add_task(task: str):
    try:
        global day_data
        global now
        global display_date
        db.add_task(task)
        day_data = db.get_day(display_date)
        return render_template('tasks.html', day_data=day_data, State=enums.State)
    except Exception as e:
        print('ERROR:', e)
        return []
    
@app.delete('/task/<string:task_ids>')
def delete_task(task_ids: str):
    try:
        global day_data
        global now
        global display_date
        db.delete_task(task_ids)
        day_data = db.get_day(display_date)
        return render_template('tasks.html', day_data=day_data, State=enums.State)

    except Exception as e:
        print('ERROR:', e)
        return [500]

@app.get('/calendar/<int:yr>')
def get_calendar(yr: int):
    global year
    task_id = request.args.get('task_id')
    year = yr if yr else now.year
    return render_template(
        'calendar.html',
        year_days=date_util.get_year_days(year, task_id=task_id),
        month_name=calendar.month_name,
        format_num=date_util.format_num,
        dt_to_str=date_util.dt_to_str,
        now=now,
        year=year,
        dark_mode=dark_mode
    )

@app.get('/day-data/<string:dt>')
def get_day_data(dt: str):
    global display_date
    global day_data
    display_date = dt
    day_data = db.get_day(display_date)
    return render_template('tasks.html', day_data=day_data, State=enums.State)

@app.put('/task-name/<int:task_id>/<string:task_name>')
def change_task_name(task_id: int, task_name: str):
    global day_data
    global now
    global display_date
    db.change_task_name(task_id, task_name)
    day_data = db.get_day(display_date)
    return render_template('tasks.html', day_data=day_data, State=enums.State)

@app.get('/bottom-text')
def get_bottom_text():
    """API endpoint to get the bottom text"""
    return jsonify({'text': db.get_bottom_text()})

@app.post('/bottom-text')
def save_bottom_text():
    """API endpoint to save the bottom text"""
    try:
        text = request.json.get('text', '')
        db.set_bottom_text(text)
        return jsonify({'success': True})
    except Exception as e:
        print('ERROR:', e)
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)