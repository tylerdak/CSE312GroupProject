from __future__ import print_function
from dataclasses import replace
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

import json
import htmlElements
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

@app.route("/chat.css")
def retrieveChatStyles():
    return open('./templates/Workplace/chat.css', 'rb').read(), 200, {'Content-Type': 'text/css'}



def createLoginPage(isLoggedIn: bool, userID: string):
    renderedLogin = Templating.injectHTMLBody(srcFile="templates/Login.html")
    jsInjectableJSON = f"\"{'{'}\\\"isLoggedIn\\\":{'true' if isLoggedIn else 'false'}, \\\"userID\\\":\\\"{userID}\\\"{'}'}\""

    renderedLogin = Templating.replacePlaceholder(oldText=renderedLogin, placeholder="data",newContent=jsInjectableJSON)
    return renderedLogin

@app.route("/login", methods=['GET'])
# this assumes the user is not loggged in
def login():
    return createLoginPage(isLoggedIn=False, userID="")

@app.route("/workplace/<name>/<code>", methods=['GET'])
def open_workplace(name, code):
    # Temporary workplace backend. Just finds workplace in database
    workplace = workplaces.find({"workplace": name, "code": code})
    for each in workplace:
        chat = each.get("chat")

    users = "["
    messages = "["
    for i in range(len(chat)):
        users += "\""+ chat[i][0]+"\", "
        messages  += "\""+ chat[i][1]+"\", "
    users = users[:-2]
    messages = messages[:-2]
    users += "]"
    messages += "]"
    print(users)
    print(messages)
    outerInjected = Templating.injectHTMLBody(srcFile="./templates/Workplace/workplace.html")
    withName = replacePlaceholder(outerInjected, placeholder="name", newContent=name)
    withCode = replacePlaceholder(withName, placeholder="code", newContent=code)
    withUsers = replacePlaceholder(withCode, placeholder="users", newContent=users)
    withMessages = replacePlaceholder(withUsers, placeholder="messages", newContent=messages)
    return withMessages, 200, {'Content-Type': 'text/html'}

@app.route("/getstarted", methods=['GET'])
def getStarted():
    cookies = request.cookies
    if cookies.get('userID') == None:
        return redirect("/", code=302)
    
    renderedLogin = Templating.injectHTMLBody(srcFile="templates/JoinCreate/joincreate.html")

    return renderedLogin

@app.route("/getstarted/create/submit", methods=['POST'])
def create_workplace():
    workplaceName = request.form['Workplace Name']
    workplaceName = escape(workplaceName)
    cookies = request.cookies
    if workplaces.find_one({"userID": cookies.get('userID'), "workplace": workplaceName}) != None:
        return redirect("/getstarted", code=403)
    
    joinCode = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=20))

    
    workplaces.insert_one({"userID": cookies.get('userID'), "workplace": workplaceName, "code": joinCode, "chat": []})
    return redirect(url_for('open_workplace', name=workplaceName, code=joinCode))

@app.route("/getstarted/join/submit", methods=['POST'])
def join_workplace():
    joinCode = request.form['Join Code']
    joinCode = escape(joinCode)
    workplace = workplaces.find_one({"code": joinCode})
    if workplace == None:
        return redirect("/getstarted", code=403)

    workplace2 = workplaces.find({"code": joinCode})
    workplaceName = ""
    for each in workplace2:
        workplaceName = each.get("workplace")
    return redirect(url_for('open_workplace', name=workplaceName, code=joinCode))

@app.route("/chat-history", methods=['POST'])
def update_messages():
    data = request.data.decode().split(",")
    message = data[0]
    code = data[1]
    cookies = request.cookies

    workplace = workplaces.find({"code": code})
    chat = []
    for each in workplace:
        chat = each.get("chat")
    chat.append([cookies.get('userID'), message])
    workplaces.update_one({"code": code}, {"$set": {"chat": chat}})
    return redirect("/", code=200)

@app.route("/chat-history/<code>", methods=['GET'])
def get_messages(code):
    cookies = request.cookies
    workplace = workplaces.find({"code": code})
    chat = []
    for each in workplace:
        chat = each.get("chat")

    return redirect("/", code=200)

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

    return redirect("/")


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
            return createLoginPage(isLoggedIn=result, userID=username)

    # otherwise, fall through to the normal login html
    return createLoginPage(isLoggedIn=False, userID="")


# This function will add cover image  in login and register pages
@app.route('/Login/Cover.png', methods=['GET'])
def getCoverImage():
    return open('./templates/Login/Cover.png', 'rb').read()

@app.route('/msgIcon.png', methods=['GET'])
def getMsgIcon():
    return open('./templates/Workplace/msgIcon.png', 'rb').read(), 200, {'Content-Type': 'image/png'}

# Styles retrieval
@app.route("/styles/<stylesheet>")
def styleRetrieval(stylesheet):
    content = ''
    match stylesheet:
        case "master":
            content = open('./templates/master.css')
        case "getstarted":
            content = open('./templates/JoinCreate/joincreate.css', 'rb').read()
        case "modal":
            content = open('./templates/modal.css', 'rb').read()
        case "profile":
            content = open('./templates/Profile/profile.css','rb').read()
        case "chat":
            content = open('./templates/Workplace/chat.css','rb').read()

    return content, 200, {'Content-Type': 'text/css'}


# Script retrieval
@app.route("/scripts/<scriptname>")
def scriptRetrieval(scriptname):
    match scriptname:
        case "getstarted":
            content = open('./templates/JoinCreate/joincreate.js','rb').read()
        case "chat":
            content = open('./templates/Workplace/chat.js','rb').read()
    return content, 200, {'Content-Type':'text/js'}

@app.route("/user/<username>", methods=['GET'])
def showProfile(username):
    # Need change: hardcode username, listNameCreate, ListNameJoin
    outerInjected = Templating.injectHTMLBody(srcFile="./templates/Profile/profile.html")
    withUsername= replacePlaceholder(outerInjected, "username", username)

    userCreatedWorkspaces = workplaces.find({"userID":username})
    response = ""
    listUserCreatedWorkspaces = list(userCreatedWorkspaces)
    for wp in listUserCreatedWorkspaces:
        name: str = wp['workplace']
        code: str = wp['code']
        withName = replacePlaceholder(htmlElements.profileListedWorkspace, placeholder="workspaceName", newContent=name)
        withCode = replacePlaceholder(withName, placeholder="workspaceCode", newContent=code)
        response += withCode


    return replacePlaceholder(withUsername, placeholder="listNameCreate",newContent=response)

# moved to styleRetrieval method for coherency's sake
# @app.route("/profile.css", methods=['GET'])
# def profileCSS():
#     return open('./templates/Profile/profile.css', 'rb').read(), 200, {'Content-Type': 'text/css'}

# Site visible on http://127.0.0.1:8081/
if __name__ == "__main__":
    countStat = {"label": "viewCount"}
    countValue = {"value": 0}
    stats.update_one(countStat, {"$setOnInsert": countValue}, upsert=True)

    app.run(host="0.0.0.0", port=8081, debug=True)
