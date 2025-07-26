const State = Object.freeze({
    DONE: 1,
    PASS: 2
})

const changeState = async el => {
    let [task_id, task, hide, record_id, state_id, state, datetime] = JSON.parse(el.dataset.data.replace(/'/g, '"').replace(/None/g, 'null'))

    console.log(task_id, task, hide, record_id, state_id, state, datetime)

    stateParam = `state_id=${(state_id ?? 0)+1}`;
    recordParam = record_id ? `record_id=${record_id}` : null;
    params = [stateParam, recordParam].join('&');

    console.log(`/state/${task_id}?${params}`)
    let response = await fetch(`/state/${task_id}?${params}`, { method: 'POST' });
    console.log(response)
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
}