import sqlite3

class Database:
    def __init__(self):
        self.conn=sqlite3.connect("platform.db")
        self.conn.row_factory=sqlite3.Row
        self.cur=self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, name TEXT, message TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tasks(pendings TEXT)")

    def add_message(self,name, message):
        self.cur.execute("INSERT INTO messages(name,message) VALUES(?,?)",(name,message))
        self.conn.commit()
        self.conn.close()

    def get_messages(self):
        messages=self.cur.execute("SELECT * FROM messages ").fetchall()
        messages=[[message["name"],message["message"]] for message in messages]
        self.conn.close()
        return messages

    def add_task(self,task):
        self.cur.execute("INSERT INTO tasks(pendings) VALUES(?)",(task,))
        self.conn.commit()
        self.conn.close()

    def remove_task(self,task):
        self.cur.execute("DELETE FROM tasks WHERE pendings=?",(task,))
        self.conn.commit()
        self.conn.close()

    def get_task(self):
        tasks=self.cur.execute("SELECT * FROM tasks").fetchall()
        tasks=[task["pendings"] for task in tasks]
        self.conn.close()
        return tasks

