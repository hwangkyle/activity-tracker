# DB Information
## Tables
### records
```sql
CREATE TABLE records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT
                      UNIQUE
                      NOT NULL,
    task_id   INTEGER REFERENCES tasks (task_id) 
                      NOT NULL,
    state_id  INTEGER REFERENCES states (state_id) 
                      NOT NULL,
    datetime  TEXT    NOT NULL
                      DEFAULT (datetime() )
);
```
### tasks
```sql
CREATE TABLE tasks (
    task_id INTEGER        PRIMARY KEY AUTOINCREMENT
                           UNIQUE
                           NOT NULL,
    task    TEXT           UNIQUE
                           COLLATE NOCASE
                           NOT NULL
);
```
### states
```sql
CREATE TABLE states (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT
                     UNIQUE
                     NOT NULL,
    state    TEXT    UNIQUE
                     NOT NULL
);
```