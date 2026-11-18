from flask import Flask, request, redirect, render_template, session
from db import Database
from model import Model
from data import tributes
import random

app=Flask(__name__)
app.secret_key="secret"

@app.route("/")
def home():
    messgaes=Database().get_messages()
    return render_template("interface.html", messages=messgaes)

@app.route("/interface", methods=["GET", "POST"])
def interface():
    message=request.form.get("message")
    response=Model().classify(message)
    if response[0]=="yes":
        if response[1]=="add_task":
            
    Database().add_message("User", message)
    messages=Database().get_messages()
    return render_template("interface.html", messages=messages)
app.run(debug=True)

