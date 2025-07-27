const State = Object.freeze({
    DONE: 1,
    PASS: 2
});

let selectedTasks = new Set();

const updateCalendar = async taskIds => {
    let response = await fetch(`/calendar${ taskIds ? `?task_ids=${taskIds}` : ' '}`);
    let html = await response.text();
    document.querySelector("#calendar").innerHTML = html;
}

const changeState = async el => {
    let [task_id, task, hide, record_id, state_id, state, datetime] = JSON.parse(el.dataset.data.replace(/'/g, '"').replace(/None/g, 'null'))

    console.log(task_id, task, hide, record_id, state_id, state, datetime)

    stateParam = `state_id=${(state_id ?? 0)+1}`;
    recordParam = record_id ? `record_id=${record_id}` : null;
    params = [stateParam, recordParam].join('&');

    let response = await fetch(`/state/${task_id}?${params}`, { method: 'POST' });
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

    el.dataset.data = JSON.stringify([task_id, task, hide, record_id, new_state_id, state, datetime]);

    updateCalendar();
}

const toAddTask = async el => {
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
}

const selectTask = async el => {
    if (!el.parentElement.classList.contains('task')) return;
    let taskId = Number(el.dataset.taskid);
    if (selectedTasks.has(taskId)) {
        selectedTasks.delete(taskId);
    } else {
        selectedTasks.add(taskId);
    }

    let checked = (Number(el.dataset.checked) + 1) % 2;
    el.dataset.checked = checked;
    el.classList.toggle('checked');
}

const deleteTasks = async () => {
    if (selectedTasks.size === 0) return;
    if (confirm(`Are you sure you want to delete ${selectedTasks.size} task(s)?`)); {
        let taskIds = [...selectedTasks].join(',');
        let response = await fetch(`/task/${taskIds}`, { method: 'DELETE' });
        selectedTasks.clear();
        let html = await response.text();
        document.querySelector("#tasks").innerHTML = html;
        updateCalendar();
    }
}

const viewTasks = async () => {
    let taskIds = [...selectedTasks].join(',');
    updateCalendar(taskIds);
    document.querySelectorAll('.select-box').forEach(element => {
        element.classList.remove('checked');
        element.nextElementSibling.classList.remove('bold');
        if (selectedTasks.has(Number(element.dataset.taskid))) {
            element.nextElementSibling.classList.add('bold');
        }
    });
    selectedTasks.clear();
}