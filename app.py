from flask import Flask, request, redirect, render_template, session
from db import Database
from model import Model
from data import tributes
import random

app=Flask(__name__)
app.secret_key="secret"

@app.route("/")
def home():
    convo_messages=Database().get_messages()
    convo_pins=Database().get_highlight()
    if convo_pins:
        return render_template("interface.html", messages=convo_messages, pins=convo_pins)
    return render_template("interface.html", messages=convo_messages)

@app.route("/interface", methods=["GET", "POST"])
def interface():
    message=request.form.get("message")
    response=Model().classify(message)
    Database().add_message("User", message)
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

    convo_messages=Database().get_messages()
    convo_pins=Database().get_highlight()
    if convo_pins:
        return render_template("interface.html", messages=convo_messages, pins=convo_pins)
    return render_template("interface.html", messages=convo_messages)
app.run(debug=True)

