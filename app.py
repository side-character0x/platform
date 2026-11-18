from flask import Flask, request, redirect, render_template, session
from db import Database

app=Flask(__name__)
app.secret_key="secret"

@app.route("/")
def home():
    messgaes=Database().get_messages()
    return render_template("interface.html", messages=messgaes)

@app.route("/interface", methods=["GET", "POST"])
def interface():
    message=request.form.get("message")
    Database().add_message("user", message)
    messages=Database().get_messages()
    return render_template("interface.html", messages=messages)
app.run(debug=True)

