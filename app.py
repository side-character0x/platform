from flask import Flask, request, redirect, render_template, session
from db import Database
from model import Model
from data import tributes, first_message
import random
import sys
import os
import threading
import time
import webbrowser

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    template_folder = os.path.join(BASE_DIR, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__)

os.chdir(BASE_DIR)
app.secret_key="secret"

@app.route("/")
def base():
    Database().create_tables()
    return render_template("landing_page.html")

@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    username=request.form.get("username")
    valid=Database().username_validity(username)
    if valid:
        return render_template("signup.html",error=True)
    password=request.form.get("password")
    Database().add_username(username,password)
    session["username"]=username
    return redirect("/home")

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    username=request.form.get("username")
    valid=Database().username_validity(username)
    if not valid:
        return render_template("login.html",error=True)
    password=request.form.get("password")
    verify=Database().verify_password(username, password)
    if not verify:
        return render_template("login.html",error=True)
    session["username"]=username
    return redirect("/home")

@app.route("/home")
def home():
    users=Database().get_users()
    session["current_user"]=Database().get_user_id(session["username"])
    return render_template("home.html", users=users)

@app.route("/receiver", methods=["GET","POST"])
def receiver():
    receiver=request.form.get("receiver").split("/")
    session["convo_id"]=Database().get_convo_id(session["current_user"],receiver[0])
    session["receiver"]=receiver
    if receiver[0]=="1":
        return redirect("/interface")
    return chat_interface("chat.html")

@app.route("/chat_message", methods=["GET","POST"])
def chat_message():
    message=request.form.get("message")
    Database().add_message(session["convo_id"],session["current_user"],session["receiver"][0],message)
    return chat_interface("chat.html")

@app.route("/interface", methods=["GET", "POST"])
def interface():
    if request.method=="POST":
        message=request.form.get("message")
        response=Model().classify(message)
        Database().add_message(session["convo_id"],session["current_user"],session["receiver"][0],message)
        if response[0]=="yes":
            if response[1]=="add_task":
                Database().add_task(session["current_user"],response[2])
                Database().add_message(session["convo_id"],"1",session["current_user"],f"Successfully added task: {response[2]}")
            elif response[1]=="show_task":
                tasks=Database().get_task(session["current_user"])
                bot_response="Here are your tasks\n"
                for i, task in enumerate(tasks, start=1):
                    bot_response+=f"{i}. {task}\n"
                Database().add_message(session["convo_id"],"1",session["current_user"],bot_response)
            elif response[1]=="completion":
                tribute=random.choice(tributes)
                tasks=Database().get_task(session["current_user"])
                db_task=Model().task_matcher(tasks,response[2])
                if db_task[0]=="yes":
                    completed_task=db_task[1]
                    Database().remove_task(session["current_user"],completed_task)                                      #need modification
                    Database().add_message(session["convo_id"],"1",session["current_user"],f"{completed_task} marked as completed!")
                    Database().add_message(session["convo_id"],"1",session["current_user"],tribute)
            elif response[1]=="pin":
                Database().add_highlight(session["current_user"],response[2])
                Database().add_message(session["convo_id"],"1",session["current_user"],f"Pinned '{response[2]}'")
            elif response[1]=="unpin":
                pins=Database().get_highlight(session["current_user"])
                db_pin=Model().task_matcher(pins,response[2])
                if db_pin[0]=="yes":
                    unpinned=db_pin[1]
                    Database().remove_highlight(session["current_user"],unpinned)                                  #need modification
                    Database().add_message(session["convo_id"],"1",session["current_user"],f"Removed pin '{unpinned}'")
    return chat_interface("interface.html")

@app.route("/tasks", methods=["POST","GET"])
def tasks():
    if request.method=="POST":
        del_task=request.form.get("del_task")
        if del_task:
            Database().remove_task(session["current_user"],del_task)
        else:
            task=request.form.get("task")
            Database().add_task(session["current_user"],task)
    pending_tasks=Database().get_task(session["current_user"])
    users=Database().get_users()
    return render_template("tasks.html", tasks=pending_tasks,users=users)

def chat_interface(template):
    users=Database().get_users()
    current_user=session["current_user"]
    convo_messages=Database().get_messages(session["convo_id"])
    first_message_check(convo_messages,current_user)
    convo_pins=Database().get_highlight(current_user)
    if convo_pins:
        return render_template(template, messages=convo_messages, pins=convo_pins, receiver=session["receiver"][1], users=users, current_user=current_user)
    return render_template(template, messages=convo_messages, users=users, receiver=session["receiver"][1], current_user=current_user)

def first_message_check(convo_messages,current_user):
    message_count=0
    for sender,_,receiver in convo_messages:
        if sender=="2" and receiver==current_user:
            return
        if sender==current_user:
            message_count+=1
            if message_count>1:
                return
    if message_count==1:
        tribute=random.choice(first_message)
        Database().add_message(session["convo_id"],"2",current_user,tribute)
        convo_messages.append(["2",tribute])
    return

def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=True)

