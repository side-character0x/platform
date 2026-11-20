import sqlite3

class Database:
    def __init__(self):
        self.conn=sqlite3.connect("platform.db")
        self.conn.row_factory=sqlite3.Row
        self.cur=self.conn.cursor()
        agents_exists=self.cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='auth'").fetchone()
        self.cur.execute("CREATE TABLE IF NOT EXISTS auth(user_id INTEGER PRIMARY KEY, username TEXT, password INTEGER)")
        if agents_exists is None:
            agents=["Agent"]
            agents_list=[(agent,None) for agent in agents]
            self.cur.executemany("INSERT INTO auth(username,password) VALUES(?,?)", agents_list)
        self.cur.execute("CREATE TABLE IF NOT EXISTS messages(sender TEXT, receiver TEXT, message TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tasks(user TEXT, pendings TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS pins(user TEXT, highlights TEXT)")

    def get_users(self):
        users=self.cur.execute("SELECT * FROM auth WHERE user_id>1").fetchall()
        users=[[user["user_id"],user["username"]] for user in users]
        self.conn.close()
        return users
    
    def username_validity(self,username):
        db_username=self.cur.execute("SELECT * FROM auth WHERE username=?",(username,)).fetchall()
        if db_username:
            return True
        else:
            return False

    def add_username(self,username, password):
        self.cur.execute("INSERT INTO auth(username,password) VALUES(?,?)",(username,password))
        self.conn.commit()
        self.conn.close()

    def verify_password(self,username, password):
        db_password=self.cur.execute("SELECT password FROM auth WHERE username=?",(username,)).fetchone()
        if db_password==password:
            return True
        else:
            return False

    def add_message(self,sender, receiver, message):
        self.cur.execute("INSERT INTO messages(sender, receiver, message) VALUES(?,?,?)",(sender, receiver, message))
        self.conn.commit()
        self.conn.close()

    def get_messages(self):
        messages=self.cur.execute("SELECT * FROM messages ").fetchall()
        messages=[[message["sender"], message["receiver"], message["message"]] for message in messages]
        self.conn.close()
        return messages

    def add_task(self,user,task):
        self.cur.execute("INSERT INTO tasks(user, pendings) VALUES(?)",(user,task))
        self.conn.commit()
        self.conn.close()

    def remove_task(self,user,task):
        self.cur.execute("DELETE FROM tasks WHERE pendings=? AND user=?",(task,user))
        self.conn.commit()
        self.conn.close()

    def get_task(self,user):
        tasks=self.cur.execute("SELECT * FROM tasks WHERE user=?",(user,)).fetchall()
        tasks=[task["pendings"] for task in tasks]
        self.conn.close()
        return tasks

    def add_highlight(self,highlight):
        self.cur.execute("INSERT INTO pins(highlights) VALUES(?)",(highlight,))
        self.conn.commit()
        self.conn.close()

    def remove_highlight(self,highlight):
        self.cur.execute("DELETE FROM pins WHERE highlights=?",(highlight,))
        self.conn.commit()
        self.conn.close()

    def get_highlight(self,user):
        highlights=self.cur.execute("SELECT * FROM pins WHERE user=?",(user,)).fetchall()
        highlights=[highlight["highlights"] for highlight in highlights]
        self.conn.close()
        return highlights
