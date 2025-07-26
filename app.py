from flask import Flask, render_template, request
from datetime import datetime
import calendar

import db
import date_util as dt
import enums
from enums import State

app = Flask(__name__)

@app.route('/')
def index():
    now = datetime.now()
    year_days = dt.get_year_days(now.year)
    year = now.year
    active_dates = set(db.get_active_dates(now))
    tasks = db.get_tasks()

    return render_template(
        'index.html',
        year_days=year_days,
        year=year,
        now=now,
        active_dates=active_dates,
        tasks=tasks,
        month_name=calendar.month_name,
        today_data=db.get_today(),
        format_num=dt.format_num,
        State=enums.State
    )

@app.route('/state/<int:task_id>', methods=['POST'])
def update_state(task_id: int):
    state_id = int(request.args.get('state_id') or -1)
    record_id = int(request.args.get('record_id') or -1)
    print(state_id, record_id)
    if state_id == State.DONE:
        print(f"INSERT INTO records (task_id, state_id) VALUES ({task_id}, {State.DONE})")
        db._execute(f"INSERT INTO records (task_id, state_id) VALUES ({task_id}, {State.DONE})")
        record_id = db._execute("SELECT MAX(record_id) FROM records")
        return [ State.DONE, record_id ]
    elif state_id == State.PASS:
        print(f"UPDATE records SET state_id={State.PASS} WHERE record_id={record_id}")
        db._execute(f"UPDATE records SET state_id={State.PASS} WHERE record_id={record_id}")
        return [ State.PASS ]
    else:
        print(f"DELETE FROM records WHERE record_id={record_id}")
        db._execute(f"DELETE FROM records WHERE record_id={record_id}")
        return [  ]

if __name__ == '__main__':
    app.run(debug=True)