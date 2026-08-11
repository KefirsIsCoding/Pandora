import sqlite3
import os.path

class SqliteDb:
    def set_up():
        import os.path
        if os.path.isfile("pandora.db"):
            return sqlite3.connect("pandora.db")
        con = sqlite3.connect("pandora.db")
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE collection
            (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
            """
        )
        con.commit()
        cursor.execute("""
            CREATE TABLE task
            (
                id INTEGER PRIMARY KEY,
                name TEXT, 
                status TEXT, 
                progress TEXT,
                collection_id INT,
                FOREIGN KEY (collection_id) REFERENCES collection (id)
            );
            """
        )
        con.commit()
        cursor.execute("""
            CREATE TABLE subtask
            (
                id INTEGER PRIMARY KEY,
                name TEXT,
                status TEXT,
                progress TEXT,
                task_id INT,
                FOREIGN KEY (task_id) REFERENCES task (id)
            );
            """
        )
        con.commit()
        return con
