from flask import Flask, request, redirect, render_template, session
from db import Database
from model import Model
from data import tributes
import random

app=Flask(__name__)
app.secret_key="secret"

@app.route("/")
def base():
    return render_template("login.html")

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
    session["receiver"]=receiver
    return redirect("/chat")

@app.route("/chat", methods=["GET","POST"])
def chat():
    current_user=session["current_user"]
    messages=Database().get_messages(current_user,session["receiver"][0])
    users=Database().get_users()
    return render_template("chat.html",messages=messages,current_user=current_user, receiver=session["receiver"][1],users=users)

@app.route("/chat_message", methods=["GET","POST"])
def chat_message():
    message=request.form.get("message")
    Database().add_message(session["current_user"],session["receiver"][0],message)
    return redirect("/chat")

@app.route("/interface", methods=["GET", "POST"])
def interface():
    if request.method=="POST":
        message=request.form.get("message")
        response=Model().classify(message)
        Database().add_message(session["current_user"],session["receiver"][0],message)
        if response[0]=="yes":
            if response[1]=="add_task":
                Database().add_task(response[2])
                Database().add_message("Task Manager",f"Successfully added task: {response[2]}")
            elif response[1]=="show_task":
                tasks=Database().get_task()
                bot_response="Here are your tasks\n"
                for i, task in enumerate(tasks, start=1):
                    bot_response+=f"{i}. {task}\n"
                Database().add_message("Task Manager",bot_response)
            elif response[1]=="completion":
                tribute=random.choice(tributes)
                tasks=Database().get_task()
                db_task=Model().task_matcher(tasks,response[2])
                if db_task[0]=="yes":
                    completed_task=db_task[1]
                    Database().remove_task(completed_task)                                      #need modification
                    Database().add_message("Task Manager",f"{completed_task} marked as completed!")
                    Database().add_message("Task Manager",tribute)
            elif response[1]=="pin":
                Database().add_highlight(response[2])
                Database().add_message("Pins Manager",f"Pinned '{response[2]}'")
            elif response[1]=="unpin":
                pins=Database().get_highlight()
                db_pin=Model().task_matcher(pins,response[2])
                if db_pin[0]=="yes":
                    unpinned=db_pin[1]
                    Database().remove_highlight(unpinned)                                  #need modification
                    Database().add_message("Pins Manager",f"Removed pin '{unpinned}'")
    agent=1
    users=Database().get_users()
    current_user=session["current_user"]
    convo_messages=Database().get_messages(current_user,agent)
    convo_pins=Database().get_highlight()
    if convo_pins:
        return render_template("interface.html", messages=convo_messages, pins=convo_pins, users=users)
    return render_template("interface.html", messages=convo_messages, users=users)

@app.route("/tasks", methods=["POST","GET"])
def tasks():
    if request.method=="POST":
        del_task=request.form.get("del_task")
        if del_task:
            Database().remove_task(del_task)
        else:
            task=request.form.get("task")
            Database().add_task(task)
    pending_tasks=Database().get_task()
    return render_template("tasks.html", tasks=pending_tasks)
app.run(debug=True)

