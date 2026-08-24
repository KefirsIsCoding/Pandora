from .consts import Status

class Collection:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def save(db, name):
        db.cursor().execute(f"INSERT INTO collection (name) VALUES('{name}');")
        db.commit()

    def edit(db, name, id):
        db.cursor().execute("""UPDATE collection SET name = ? WHERE id = ?""", (name, id))
        db.commit()

    def delete(db, id):
        db.cursor().execute("""DELETE FROM collection WHERE id = ?""", (id,))
        db.commit()

    def get_all(db):
        return [
            Collection(id, name) for id, name in
            db.cursor().execute("SELECT * FROM collection ORDER BY id").fetchall()
        ]

class Task:
    def __init__(self, id, name, status, progress, collection_id, fields):
        self.id = id
        self.name = name
        self.status = status
        self.progress = progress
        self.collection_id = collection_id
        self.custom_fields = fields

    def save(db, name, collection):
        db.cursor().execute("""
            INSERT INTO task (name, collection_id) VALUES (?, ?);""",
            (name, collection)
        )
        db.commit()

    def delete(db, id):
        db.cursor().execute("DELETE FROM task WHERE id =?", (id,))
        db.commit()

    def edit(db, name, id, fields):
        db.cursor().execute("UPDATE task SET name = ? WHERE id = ?", (name, id))
        db.commit()
        task_fields = CustomFields.get_task_fields(db, id)
        new_fields = [(x.get("id", None), x.get("name").get(), x.get("value").get()) for x in fields.values()]
        is_full = len(task_fields) == 3
        ### Del
        for tf in task_fields:

            if tf.id not in [b[0] for b in new_fields]:
                CustomFields.delete(db, tf.id)
        for values in fields.values():
            # Wipe if exists
            if id_val := values.get("id"):
                db.cursor().execute("""
                    UPDATE customfields SET name = ?, value = ? WHERE id = ?
                """, (values.get("name").get(), values.get("value").get(), values.get("id")))
                db.commit()
            else:
                db.cursor().execute("""
                    INSERT INTO customfields (name, value, task_id) VALUES (?, ?, ?);
                """, (values.get("name").get(), values.get("value").get(), id))
                db.commit()

    def _resolve_progress(total, done):
        return f'{done}/{total}' if total else "No subtasks"

    def _resolve_status(total, backlog, wip, done):
        if wip:
            return Status.WIP.name
        elif done == total and total > 0:
            return Status.DONE.name
        else:
            return Status.BACKLOG.name

    def get_all(db):
        return [
            Task(id, name, _resolve_progress(s_c, s_d), _resolve_status(s_c, s_b, s_w, s_d),collection_id)
            for id, name, s_c, s_b, s_wip, s_d, collection_id in
            db.cursor().execute("""
                SELECT
                    t.id,
                    t.name,
                    Count(s.id),
                    Sum(Iif(s.status = 'BACKLOG',1,0)),
                    Sum(Iif(s.status = 'WIP',1,0)),
                    Sum(Iif(s.status = 'DONE',1,0)),
                    t.collection_id,
                    c.id,
                    c.name,
                    c.value
                FROM task as t
                JOIN subtask as s ON s.task_id = t.id
                JOIN customfields as c ON c.task_id = t.id
                GROUP BY t.id
            """).fetchall() if id
        ]

    def get_all_in_collection(db, c_id):
        """ o_O"""

        return [
            Task(id, name, Task._resolve_progress(s_c, s_d), Task._resolve_status(s_c, s_b, s_w, s_d),collection_id, CustomFields.get_task_fields(db, id))
            for id, name, s_c, s_b, s_w, s_d, collection_id in
                db.cursor().execute("""
                SELECT
                    t.id,
                    t.name,
                    Count(s.id),
                    Sum(Iif(s.status = 'BACKLOG',1,0)),
                    Sum(Iif(s.status = 'WIP',1,0)),
                    Sum(Iif(s.status = 'DONE',1,0)),
                    t.collection_id
                FROM task as t
                LEFT JOIN subtask as s ON s.task_id = t.id
                WHERE t.collection_id = ?
                GROUP BY t.id
                """, (c_id,)).fetchall() if id
        ]

class SubTask:
    def __init__(self, id, name, task, repeat, date, status=Status.BACKLOG, progress=None):
        self.id = id
        self.name = name
        self.status = status
        self.progress = progress
        self.task_id = task
        self.repeat = repeat
        self.date = date

    def save(db, name, task_id, repeat, date, status=Status.BACKLOG, progress=None):
        db.cursor().execute("""
            INSERT INTO subtask (name, status, progress, task_id, repeat, date) VALUES(?,?,?,?,?,?);""",
            (name, status.name, progress,task_id, repeat, date)
        )
        db.commit()

    def edit(db, id, name, progress, status, repeat, date):
        db.cursor().execute("""
            UPDATE subtask SET name = ?, progress = ?, status = ?, repeat = ?, date = ? WHERE id = ?;
            """,
            (name,progress,status,repeat, date, id)
        )
        db.commit()

    def set_status(db, id, status):
        db.cursor().execute("UPDATE subtask SET status = ? WHERE id = ?", (status, id))
        db.commit()

    def delete(db, id):
        db.cursor().execute("DELETE from subtask WHERE id= ?;", (id,))
        db.commit()

    def get_all(db):
        return [
            SubTask(id, name, task_id, repeat, date, status, progress) for id, name, status, progress, task_id, repeat, date in
            db.cursor().execute("SELECT * FROM subtask;").fetchall()
        ]

    def get_all_in_task(db, id):
        return [
            SubTask(id, name, task_id, repeat, date, status, progress) for id, name, status, progress, task_id,repeat, date in
            db.cursor().execute("""
            SELECT id, name, status, progress, task_id, repeat, date
            FROM subtask WHERE task_id = ?""", (id,)).fetchall()
        ]

class Agenda:
    def __init__(self, task, subtasks):
        self.title = task.name
        self.tasks = [subt.name for subt in subtasks]

    def get_agenda_list(db):
        agenda_list = dict()
        for task_name, subtask_name, subtask_id, subtask_repeat, subtask_due in db.cursor().execute("""
            SELECT task.name, subtask.name, subtask.id, subtask.repeat, subtask.date FROM task JOIN subtask
            WHERE task.id=subtask.task_id AND subtask.status = ?;""", ("WIP",)).fetchall():
            if agenda_list.get(task_name):
                agenda_list[task_name][subtask_id] = [subtask_name, subtask_repeat, subtask_due]
            else:
                agenda_list[task_name] = {subtask_id : [subtask_name, subtask_repeat, subtask_due]}
        return agenda_list


class CustomFields:
    """Extra StringField fields"""
    def __init__(self, id, name, value):
        self.id = id
        self.name = name
        self.value = value

    def get_task_fields(db, task_id):
        return [
            CustomFields(id, name, value) for id, name, value in
            db.cursor().execute("""
                SELECT id, name, value FROM customfields 
                WHERE task_id = ?;
                """, (task_id,)).fetchall()
                ]
    def delete(db, id):
        db.cursor().execute("""
            DELETE FROM customfields WHERE id = ?
        """, (id,))
        db.commit()
