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
                collection_id INT,
                FOREIGN KEY (collection_id) REFERENCES collection (id) ON DELETE CASCADE
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
                repeat INT,
                date TEXT,
                FOREIGN KEY (task_id) REFERENCES task (id) ON DELETE CASCADE
            );
            """
        )
        con.commit()
        # Enables foreign key contraints (On DELETE)
        con.execute("PRAGMA foreign_keys = 1")
        con.commit()
        return con
