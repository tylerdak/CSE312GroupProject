from __future__ import print_function
import sys
import flask
from flask import Flask, request, redirect, url_for, render_template
from pymongo import MongoClient
import random
import string
# Custom Password Manager Class
from crypt import PassMan

from templating import Templating
import verify

# import json
# from numpy import place
# import pymongo

app = Flask(__name__)

# client = MongoClient("mongodb+srv://cse312group:db@cluster0.u70wkht.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient("mongo")
db = client["CSE312Group"]
stats = db["stats"]
users = db["users"]
workplaces = db["workplaces"]


def escape(htmlStr):
    return htmlStr.replace("&", "&amp").replace("<", "&lt").replace(">", "&gt")


def replacePlaceholder(oldText: str, placeholder: str, newContent: str):
    return oldText.replace("{{" + placeholder + "}}", newContent)


# Add viewCount retrieval code here
#
# I've added code to replace placeholders with whatever
# you end up returning in this function (ideally a correct
# page count)
def getCurrentPageViewCount():
    return stats.find_one({"label": "viewCount"})['value']


def incrementPageViewCount():
    counter = getCurrentPageViewCount()
    stats.update_one({"label": "viewCount"}, {"$set": {"value": counter + 1}})
    return counter + 1


@app.route("/")
def index():
    # may want later
    #
    # all_users = list(users.find({}, {'email': 1, '_id': 0}))
    # all_users_list = []
    # for x in all_users:
    #     email_insert = "Email: ", x.get("email")
    #     all_users_list.insert(0, email_insert)

    return Templating.injectHTMLBody(None, srcFile="templates/index.html")

@app.route("/registerLoginStyles.css")
def retrieveRegisterLoginStyles():
    return open('./templates/registerLoginStyles.css', 'rb').read(), 200, {'Content-Type': 'text/css'}



def createLoginPage(isLoggedIn: bool):
    renderedLogin = Templating.injectHTMLBody(srcFile="templates/Login.html")
    jsInjectableJSON = f"\"{'{'}\\\"isLoggedIn\\\":{'true' if isLoggedIn else 'false'}{'}'}\""
    renderedLogin = Templating.replacePlaceholder(oldText=renderedLogin, placeholder="data",newContent=jsInjectableJSON)
    return renderedLogin

@app.route("/login", methods=['GET'])
# this assumes the user is not loggged in
def login():
    return createLoginPage(isLoggedIn=False)

@app.route("/workplace/<name>", methods=['GET'])
def open_workplace(name):
    workplace = workplaces.find({"workplace": name})
    for each in workplace:
        code = each.get("code")
    return render_template('Workplace/workplace.html', name=name, code=code)

@app.route("/getstarted", methods=['GET'])
def getStarted():
    renderedLogin = Templating.injectHTMLBody(srcFile="templates/JoinCreate/joincreate.html")

    return renderedLogin

@app.route("/getstarted/create/submit", methods=['POST'])
def create_workplace():
    workplaceName = request.form['Workplace Name']
    
    if workplaces.find_one({"workplace": workplaceName}) != None:
        return redirect("/getstarted", code=403)
    
    joinCode = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=20))
    workplaces.insert_one({"workplace": workplaceName, "code": joinCode})
    return redirect(url_for('open_workplace', name=workplaceName))

@app.route("/getstarted/join/submit", methods=['POST'])
def join_workplace():
    joinCode = request.form['Join Code']
    
    workplace = workplaces.find_one({"code": joinCode})
    if workplace == None:
        return redirect("/getstarted", code=403)

    workplace2 = workplaces.find({"code": joinCode})
    workplaceName = ""
    for each in workplace2:
        workplaceName = each.get("workplace")
    return redirect(url_for('open_workplace', name=workplaceName))


@app.route('/', methods=['POST'])
def insert_display_index():
    username = request.form['username']
    password = request.form['psw']
    password_result = verify.validate.verify_password(password)      # return True or False
    username_result = verify.validate.verify_username(username)
    if password_result:
        if username_result:
            users.insert_one({"username": username, "password": PassMan.hash(password.encode())})
            print("Your account has been created successfully")
            return redirect("/login", code=302)
        else:
            print("Please edit the username")
    else:
        print("Please edit the password")

    return redirect("/", code=302)


@app.route('/login', methods=['POST'])
def insert_display_login():
    username = request.form['username']
    password = request.form['psw']

    proposedUser = users.find_one({"username":username})
    if proposedUser is None:
        print("User does not exist")
    else:
        hashedPassword = proposedUser["password"]
        result = PassMan.check(password.encode(), hashedPassword)
        # if password is correct, tell JS to send the user to the /getstarted
        # and store the cookie
        if result is True:
            return createLoginPage(isLoggedIn=result)

    # otherwise, fall through to the normal login html
    return createLoginPage(isLoggedIn=False)


# This function will add cover image  in login and register pages
@app.route('/Login/Cover.png', methods=['GET'])
def getCoverImage():
    return open('./templates/Login/Cover.png', 'rb').read()

# Styles retrieval
@app.route("/styles/<stylesheet>")
def styleRetrieval(stylesheet):
    match stylesheet:
        case "master":
            content = open('./templates/master.css')
        case "getstarted":
            content = open('./templates/JoinCreate/joincreate.css', 'rb').read()
        case "modal":
            content = open('./templates/modal.css', 'rb').read()

    return content, 200, {'Content-Type': 'text/css'}

# Script retrieval
@app.route("/scripts/<scriptname>")
def scriptRetrieval(scriptname):
    match scriptname:
        case "getstarted":
            content = open('./templates/JoinCreate/joincreate.js','rb').read()
    return content, 200, {'Content-Type':'text/js'}

# Site visible on http://127.0.0.1:8081/
if __name__ == "__main__":
    countStat = {"label": "viewCount"}
    countValue = {"value": 0}
    stats.update_one(countStat, {"$setOnInsert": countValue}, upsert=True)

    app.run(host="0.0.0.0", port=8081, debug=True)
