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
    def __init__(self, id, name, status, progress, collection_id):
        self.id = id
        self.name = name
        self.status = status
        self.progress = progress
        self.collection_id = collection_id

    def save(db, name, collection):
        db.cursor().execute("""
            INSERT INTO task (name, collection_id) VALUES (?, ?);""",
            (name, collection)
        )
        db.commit()

    def delete(db, id):
        db.cursor().execute("DELETE FROM task WHERE id =?", (id,))
        db.commit()

    def edit(db, name, id):
        db.cursor().execute("UPDATE task SET name = ? WHERE id = ?", (name, id))
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
                    t.collection_id
                FROM task as t
                JOIN subtask as s ON s.task_id = t.id
                GROUP BY t.id
            """).fetchall() if id
        ]

    def get_all_in_collection(db, c_id):
        """ o_O"""
        return [
            Task(id, name, Task._resolve_progress(s_c, s_d), Task._resolve_status(s_c, s_b, s_w, s_d),collection_id)
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
    def __init__(self, id, name, task, status=Status.BACKLOG, progress=None):
        self.id = id
        self.name = name
        self.status = status
        self.progress = progress
        self.task_id = task

    def save(db, name, task_id, status=Status.BACKLOG, progress=None):
        db.cursor().execute("""
            INSERT INTO subtask (name, status, progress, task_id) VALUES(?,?,?,?);""",
            (name, status.name, progress,task_id)
        )
        db.commit()

    def edit(db, id, name, progress, status):
        db.cursor().execute("""
            UPDATE subtask SET name = ?, progress = ?, status = ? WHERE id = ?;
            """,
            (name,progress,status,id)
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
            SubTask(id, name, task_id, status, progress) for id, name, status, progress, task_id in
            db.cursor().execute("SELECT * FROM subtask;").fetchall()
        ]

    def get_all_in_task(db, id):
        return [
            SubTask(id, name, task_id, status, progress) for id, name, status, progress, task_id in
            db.cursor().execute("""
            SELECT id, name, status, progress, task_id
            FROM subtask WHERE task_id = ?""", (id,)).fetchall()
        ]

class Agenda:
    def __init__(self, task, subtasks):
        self.title = task.name
        self.tasks = [subt.name for subt in subtasks]

    def get_agenda_list(db):
        agenda_list = dict()
        for task_name, subtask_name, subtask_id in db.cursor().execute("""
            SELECT task.name, subtask.name, subtask.id FROM task JOIN subtask
            WHERE task.id=subtask.task_id AND subtask.status = ?;""", ("WIP",)).fetchall():
            if agenda_list.get(task_name):
                agenda_list[task_name][subtask_id] = subtask_name
            else:
                agenda_list[task_name] = {subtask_id : subtask_name}
        return agenda_list
