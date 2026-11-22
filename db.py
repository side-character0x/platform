import sqlite3

class Database:
    def __init__(self):
        self.conn=sqlite3.connect("platform.db")
        self.conn.row_factory=sqlite3.Row
        self.cur=self.conn.cursor()

    def create_tables(self):
        agents_exists=self.cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='auth'").fetchone()
        self.cur.execute("CREATE TABLE IF NOT EXISTS auth(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
        if agents_exists is None:
            agents=["Agents","Herald"]
            agents_list=[(agent,None) for agent in agents]
            self.cur.executemany("INSERT INTO auth(username,password) VALUES(?,?)", agents_list)
        self.cur.execute("CREATE TABLE IF NOT EXISTS messages(sender TEXT, receiver TEXT, message TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tasks(user TEXT, pendings TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS pins(user TEXT, highlights TEXT)")
        self.conn.commit()
        self.conn.close()

    def get_users(self):
        users=self.cur.execute("SELECT * FROM auth WHERE user_id>2").fetchall()
        users=[[user["user_id"],user["username"]] for user in users]
        self.conn.close()
        return users

    def get_user_id(self,username):
        id=self.cur.execute("SELECT user_id FROM auth WHERE username=?",(username,)).fetchone()
        self.conn.close()
        user_id=str(id["user_id"])
        return user_id

    def username_validity(self,username):
        db_username=self.cur.execute("SELECT * FROM auth WHERE username=?",(username,)).fetchall()
        self.conn.close()
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
        self.conn.close()
        print(type(db_password["password"]),type(password))
        if db_password["password"]==password:
            return True
        else:
            return False

    def add_message(self,sender, receiver, message):
        self.cur.execute("INSERT INTO messages(sender, receiver, message) VALUES(?,?,?)",(sender, receiver, message))
        self.conn.commit()
        self.conn.close()

    def get_messages(self,party_1,party_2):
        messages=self.cur.execute("SELECT * FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) OR (sender=? AND receiver=?)",(party_1,party_2,party_2,party_1,"2",party_1)).fetchall()
        messages=[[message["sender"], message["message"], message["receiver"]] for message in messages]
        self.conn.close()
        return messages

    def add_task(self,user,task):
        self.cur.execute("INSERT INTO tasks(user, pendings) VALUES(?,?)",(user,task))
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

    def add_highlight(self,user,highlight):
        self.cur.execute("INSERT INTO pins(user,highlights) VALUES(?,?)",(user,highlight))
        self.conn.commit()
        self.conn.close()

    def remove_highlight(self,user,highlight):
        self.cur.execute("DELETE FROM pins WHERE highlights=? AND user=?",(highlight,user))
        self.conn.commit()
        self.conn.close()

    def get_highlight(self,user):
        highlights=self.cur.execute("SELECT * FROM pins WHERE user=?",(user,)).fetchall()
        highlights=[highlight["highlights"] for highlight in highlights]
        self.conn.close()
        return highlights
