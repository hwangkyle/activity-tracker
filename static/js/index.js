const debug = true; // Use as necessary

const State = Object.freeze({
    DONE: 1,
    PASS: 2
});

let currViewedTask = '';

let [__month, __day, __year] = new Date().toLocaleString().split(/,? /g)[0].split('/').map(val => val.length === 1 ? `0${val}` : val);
let today = `${__year}-${__month}-${__day}`
let currViewedDt = `${__year}-${__month}-${__day}`;

const updateCalendar = async (taskIds, useCurr=true) => {
    taskParam = '';
    if (taskIds) taskParam = `?task_ids=${taskIds}`;
    else if (useCurr && currViewedTask) taskParam = `?task_ids=${currViewedTask}`;
    let path = `/calendar${taskParam}`;
    if (debug) console.log(path);
    let response = await fetch(path);
    let html = await response.text();
    document.querySelector("#calendar").innerHTML = html;
    maintainViews();
}

const changeState = async el => {
    if (today !== currViewedDt) return;
    let [task_id, task, record_id, state_id, state, datetime] = JSON.parse(el.dataset.data.replace(/'/g, '"').replace(/None/g, 'null'))

    stateParam = `state_id=${(state_id ?? 0)+1}`;
    recordParam = record_id ? `record_id=${record_id}` : null;
    params = [stateParam, recordParam].join('&');

    let response = await fetch(`/state/${task_id}/${currViewedDt}?${params}`, { method: 'POST' });
    let [ new_state_id, new_record_id ] = await response.json();

    if (new_state_id === State.DONE) {
        el.classList.add('done');
        el.classList.remove('pass');
        record_id = new_record_id;
    } else if (new_state_id === State.PASS) {
        el.classList.remove('done');
        el.classList.add('pass');
    } else {
        el.classList.remove('pass');
        el.classList.remove('done');
    }

    el.dataset.data = JSON.stringify([task_id, task,  record_id, new_state_id, state, datetime]);

    await updateCalendar();
}

const toAddTask = el => {
    let svg = el.children[0];
    let input = el.children[1];

    svg.classList.add('hide');
    input.classList.remove('hide');
    input.focus();
}

const addTask = async el => {
    let svg = el.parentElement.children[0];
    svg.classList.remove('hide');
    el.classList.add('hide');

    if (el.value.trim() === '') return;
    let response = await fetch(`/task/${el.value}`, { method: 'POST' });
    let html = await response.text();
    el.value = '';

    document.querySelector("#tasks").innerHTML = html;
    maintainViews();
}

const viewTask = async el => {
    let taskId = el.dataset.taskid;
    if (currViewedTask === taskId) {
        await updateCalendar(null, false);
        document.querySelector(`#view-task-${taskId} .yes-view`).classList.add('hide');
        document.querySelector(`#view-task-${taskId} .no-view`).classList.remove('hide');
        currViewedTask = '';
    } else {
        await updateCalendar(taskId);
        try {
            document.querySelector(`#view-task-${currViewedTask} .yes-view`).classList.add('hide');
            document.querySelector(`#view-task-${currViewedTask} .no-view`).classList.remove('hide');
        } catch { }
        document.querySelector(`#view-task-${taskId} .yes-view`).classList.remove('hide');
        document.querySelector(`#view-task-${taskId} .no-view`).classList.add('hide');
        currViewedTask = taskId;
    }
}

const deleteTask = async el => {
    let taskId = el.dataset.taskid;
    let taskName = el.dataset.taskname;
    if (confirm(`Are you sure you want to delete ${taskName}? (This will permanently delete all history with this task!)`)) {
        let response = await fetch(`/task/${taskId}`, { method: 'DELETE' });
        let html = await response.text();
        document.querySelector("#tasks").innerHTML = html;
        updateCalendar();
    }
}

const toChangeTaskName = el => {
    let taskId = el.dataset.taskid;
    document.querySelector(`#task-options-${taskId}`).classList.add('hide');
    document.querySelector(`#task-name-${taskId}`).classList.add('hide');
    let input = document.querySelector(`#task-name-input-${taskId}`);
    input.classList.remove('hide');
    input.focus();
}

const changeTaskName = async el => {
    let taskId = el.dataset.taskid;
    let input = document.querySelector(`#task-name-input-${taskId}`);
    let taskName = input.value;
    let options = document.querySelector(`#task-options-${taskId}`);
    let taskNameEl = document.querySelector(`#task-name-${taskId}`);
    if (taskName.trim() !== '' && taskName !== el.dataset.taskname) {
        let response = await fetch(`/task-name/${taskId}/${taskName}`, { method: 'PUT' });
        let html = await response.text();
        document.querySelector("#tasks").innerHTML = html;
        maintainViews();
    } else {
        options.classList.remove('hide');
        taskNameEl.classList.remove('hide');
        input.classList.add('hide');
        input.value = el.dataset.taskname;
    }
}

const getDayData = async el => {
    let dt = el.dataset.date;
    let response = await fetch(`/day-data/${dt}`);
    let html = await response.text();
    document.querySelector("#tasks").innerHTML = html;
    document.querySelector(`#date-${currViewedDt}`).classList.remove('viewing');
    document.querySelector(`#date-${dt}`).classList.add('viewing');
    currViewedDt = dt;
    if (today !== currViewedDt) {
        document.querySelectorAll('.task').forEach(el => el.classList.add('null'));
        document.querySelectorAll('.task-options').forEach(el => el.classList.add('hide'));
        document.querySelector('.task.add-task').classList.add('hide');
    }
    maintainViews();
}

const maintainViews = () => {
    localMaintainCalendarView();
    localMaintainTaskView();
}

const localMaintainCalendarView = () => {
    document.querySelector(`#date-${today}`).classList.remove('viewing');
    document.querySelector(`#date-${currViewedDt}`).classList.add('viewing');
    
    let [__month, __day, __year] = new Date().toLocaleString().split(/,? /g)[0].split('/').map(val => val.length === 1 ? `0${val}` : val);
    let _today = `${__year}-${__month}-${__day}`
    if (today !== _today) {
        document.querySelector(`#date-${today}`).classList.remove('today');
        document.querySelector(`#date-${_today}`).classList.add('today');
        today = _today;
    }
}

const localMaintainTaskView = () => {
    if (currViewedTask !== '') {
        document.querySelector(`#view-task-${currViewedTask} .yes-view`).classList.remove('hide');
        document.querySelector(`#view-task-${currViewedTask} .no-view`).classList.add('hide');
    }
}

function runAtMidnight(callback) {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(now.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0); // Set to midnight
    
    const msUntilMidnight = tomorrow.getTime() - now.getTime();
    
    setTimeout(callback, msUntilMidnight);
}

runAtMidnight(localMaintainCalendarView);