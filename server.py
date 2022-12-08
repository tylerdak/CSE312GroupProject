from __future__ import print_function
from dataclasses import replace
import datetime
import sys
import flask
from flask import Flask, request, redirect, url_for, render_template, make_response
from flask_socketio import SocketIO, join_room, leave_room
from dbstuff import *
import random
import string
# Custom Password Manager Class

# parse timestamps back to dates
import dateutil.parser

from templating import Templating
import verify

from Private import flask_secret_key
from cryptStuff import PassMan, AuthTokenPair, AuthToken
import json
import htmlElements
# from numpy import place
# import pymongo

app = Flask(__name__)
app.config['SECRET_KEY'] = flask_secret_key
socketio = SocketIO(app=app)

# client = MongoClient("mongodb+srv://cse312group:db@cluster0.u70wkht.mongodb.net/?retryWrites=true&w=majority")

standardRedirect = redirect("/")


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
    response = make_response(Templating.injectHTMLBody(None, srcFile="templates/index.html"))
    response.set_cookie("auth","jk that's not what this is",max_age=0)
    return response

@app.route("/registerLoginStyles.css")
def retrieveRegisterLoginStyles():
    return open('./templates/registerLoginStyles.css', 'rb').read(), 200, {'Content-Type': 'text/css'}

@app.route("/chat.css")
def retrieveChatStyles():
    return open('./templates/Workplace/chat.css', 'rb').read(), 200, {'Content-Type': 'text/css'}



def createLoginPage(isLoggedIn: bool, authToken: string):
    renderedLogin = Templating.injectHTMLBody(srcFile="templates/Login.html")
    return renderedLogin

@app.route("/login/", methods=['GET'])
def login():
    auth = request.cookies.get('auth')
    if not AuthToken.validAuthToken(authCookie=auth):
        pass
    else:
        # verify that the auth token belongs to a user
        if AuthToken.getUsernameFromAuthToken(authToken=auth) != None:
            # user is already authenticated, send them to /getstarted
            return redirect("/getstarted")
        else:
            print("This auth token might have been outdated... Either way it's not valid.")
    response = make_response(createLoginPage(isLoggedIn=False, authToken=""))
    response.set_cookie("auth","jk that's not what this is", max_age=0)
    return response

@app.route("/workplace/<code>/", methods=['GET'])
def open_workplace(code):
    authToken = request.cookies.get("auth")
    if not AuthToken.validAuthToken(authCookie=authToken):
        return redirect("/")

    # Temporary workplace backend. Just finds workplace in database
    workplace = workplaces.find_one({"code": code})

    usersArr = workplace.get("users")
    resultingUsername = AuthToken.getUsernameFromAuthToken(authToken)
    alreadyJoined = False
    if usersArr is not None and resultingUsername in usersArr:
        alreadyJoined = True
    elif usersArr is None:
        usersArr = []
    if(alreadyJoined == False):
        usersArr.append(resultingUsername)
        workplaces.update_one({'code': code}, {'$set': {'users': usersArr}})

    chat = []
    chatGet = workplace.get("chat")
    if chatGet != None:
        chat = chatGet

    usersArray = "["
    messagesArray = "["
    if chat != []:
       
        for i in range(len(chat)):
            usersArray += "\""+ chat[i][0]+"\", "
            messagesArray  += "\""+ chat[i][1]+"\", "
        usersArray = usersArray[:-2]
        messagesArray = messagesArray[:-2]
    usersArray += "]"
    messagesArray += "]"

    wpUsers = []
    usersGet = workplace.get("users")
    ownerGet = workplace.get("userID")
    if usersGet != None:
        wpUsers = usersGet
    wpUsersArray = "["
    wpUsersVote = "["
    if wpUsers != []:
        for i in range(len(wpUsers)):
            wpUsersArray += "\""+ wpUsers[i]+"\", "
            #Temporary implementation: str(0) must be changed to total votes once implemented
            wpUsersVote += "\""+ str(0)+"\", "

        wpUsersArray = wpUsersArray[:-2]
        wpUsersVote = wpUsersVote[:-2]

        wpUsersArray += ", \"" + code +"\""
    wpUsersArray += "]"
    wpUsersVote += "]"

    outerInjected = Templating.injectHTMLBody(srcFile="./templates/Workplace/workplace.html")
    withName = replacePlaceholder(outerInjected, placeholder="name", newContent=workplace.get("workplace"))
    withCode = replacePlaceholder(withName, placeholder="code", newContent=code)
    withUsers = replacePlaceholder(withCode, placeholder="users", newContent=usersArray)
    withMessages = replacePlaceholder(withUsers, placeholder="messages", newContent=messagesArray)
    withVotes = replacePlaceholder(withMessages, placeholder="totalvotes", newContent=wpUsersVote)
    withWpUsers = replacePlaceholder(withVotes, placeholder="workplaceusers", newContent=wpUsersArray)

    withSendQuestionInput = None
    withSendQuestionButton = None

    username = AuthToken.getUsernameFromAuthToken(authToken=request.cookies.get("auth"))
    if username == workplace["userID"]:
        withSendQuestionInput = replacePlaceholder(withWpUsers, placeholder="sendQuestionInput", newContent='<input type="text" id="questionInput" placeholder="Type question here..." />')
        withSendQuestionButton = replacePlaceholder(withSendQuestionInput, placeholder="sendQuestion", newContent='<span onclick="sendQuestion();" class="addBtn">Submit</span>')
        withSendQuestionButton = replacePlaceholder(withSendQuestionButton, placeholder="questionExpiryInput", newContent='<input type="text" id="questionExpiryInput" placeholder="Amount of time for question in seconds (default: 60s)" />')
        withSendQuestionButton = replacePlaceholder(withSendQuestionButton, placeholder="timer", newContent='<span class="expiredTimer" id="timerThing">EXPIRED</span>')
    else:
        withSendQuestionInput = replacePlaceholder(withWpUsers, placeholder="sendQuestionInput", newContent='<input type="text" id="questionInput" placeholder="Waiting for question" disabled/>')
        withSendQuestionButton = replacePlaceholder(withSendQuestionInput, placeholder="sendQuestion", newContent='<span class="expiredTimer" id="timerThing">EXPIRED</span>')
        # empty content
        withSendQuestionButton = replacePlaceholder(withSendQuestionButton, placeholder="questionExpiryInput", newContent='')
        withSendQuestionButton = replacePlaceholder(withSendQuestionButton, placeholder="timer", newContent='')

    print("RQUEST.cookies", request.cookies)

    return withSendQuestionButton, 200, {'Content-Type': 'text/html'}

@app.route("/getstarted/", methods=['GET'])
def getStarted():
    cookies = request.cookies
    if not AuthToken.validAuthToken(authCookie=cookies.get("auth")):
        return redirect("/")
    
    workplace = workplaces.find()
    wps = []
    owners = []
    codes = []
    for each in workplace:
        wps.append(each.get("workplace"))
        owners.append(each.get("userID"))
        codes.append(each.get("code"))

    workplacearray = "["
    ownersarray = "["
    codesarray = "["
    if wps != []:
        for i in range(len(wps)):
            workplacearray += "\""+ wps[i]+"\", "
            ownersarray += "\""+ owners[i]+"\", "
            codesarray += "\""+ codes[i]+"\", "
        workplacearray = workplacearray[:-2]
        ownersarray = ownersarray[:-2]
        codesarray = codesarray[:-2]
    workplacearray += "]"
    ownersarray += "]"
    codesarray += "]"
    renderedLogin = Templating.injectHTMLBody(srcFile="templates/JoinCreate/joincreate.html")
    withWorkplaces = replacePlaceholder(renderedLogin, placeholder="workplaces", newContent=workplacearray)
    withOwners = replacePlaceholder(withWorkplaces, placeholder="owners", newContent=ownersarray)
    withCodes = replacePlaceholder(withOwners, placeholder="codes", newContent=codesarray)
    return withCodes

@app.route("/getstarted/create/submit/", methods=['POST'])
def create_workplace():
    authToken = request.cookies.get("auth")
    if not AuthToken.validAuthToken(authCookie=authToken):
        return redirect("/")
    userID = AuthToken.getUsernameFromAuthToken(authToken=authToken)
    workplaceName = request.form['Workplace Name']
    workplaceName = escape(workplaceName)
    cookies = request.cookies
    if workplaces.find_one({"userID": userID, "workplace": workplaceName}) != None:
        return redirect("/getstarted")
    
    joinCode = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=20))

    workplaces.insert_one({"userID": userID, "workplace": workplaceName, "code": joinCode, "chat": [], "users": [userID]})
    return redirect(url_for('open_workplace',code=joinCode))

@app.route("/getstarted/join/submit/", methods=['POST'])
def join_workplace():
    authToken = request.cookies.get("auth")
    if not AuthToken.validAuthToken(authCookie=authToken):
        return redirect("/")
    joinCode = request.form['Join Code']
    joinCode = escape(joinCode)
    workplace = workplaces.find_one({"code": joinCode})
    if workplace == None:
        return redirect("/getstarted")

    workplace2 = workplaces.find_one({"code": joinCode})
    workplaceName = ""
    for each in workplace2:
        workplaceName = each.get("workplace")
        usersArr = each.get("users")
    resultingUsername = AuthToken.getUsernameFromAuthToken(authToken)
    alreadyJoined = False
    if usersArr is not None and resultingUsername in usersArr:
        alreadyJoined = True
    elif usersArr is None:
        usersArr = []
    if(alreadyJoined == False):
        usersArr.append(resultingUsername)
        workplaces.update_one({'code': joinCode}, {'$set': {'users': usersArr}})
    return redirect(url_for('open_workplace', code=joinCode))

def makeMessage(username: str, message: str, code: str):
    return {"username": username, "message": message, "code": code}

def update_messages(newMessageJSON: json):

   

    message = newMessageJSON["comment"]

    # the user property is = userID as of writing this
    # however, when we add auth tokens, .user will be the auth token
    # we will need to match the auth token to a userID to find the actual userID
    # do NOT send auth tokens as the userID (exposes the user's account completely)
    authToken = newMessageJSON["authToken"]
    code = newMessageJSON["workplaceCode"]

    if not AuthToken.validAuthToken(authCookie=authToken):
        socketio.emit('newMessage', {'messages': [makeMessage("[PRIVATE] SERVER",f"You are unauthorized. Your messages will not be sent. Please login first.",code=code)]}, to=request.sid)
        return

    # here's a place where you can convert the authToken to the username
    resultingUsername = AuthToken.getUsernameFromAuthToken(authToken)

    workplace = workplaces.find({"code": code})
    chat = []
    for each in workplace:
        chat = each.get("chat")
    chat.append([resultingUsername, message])
    workplaces.update_one({"code": code}, {"$set": {"chat": chat}})
    return makeMessage(resultingUsername, message, code)

@app.route('/', methods=['POST'])
def insert_display_index():
    username = escape(request.form['username'])
    password = escape(request.form['psw'])
    password_result = verify.validate.verify_password(password)      # return True or False
    username_result = verify.validate.verify_username(username)
    if password_result:
        if username_result and len(list(users.find({"username": username}))) == 0:
            # change the auth token, add a generator for it and all that
            users.insert_one({"username": username, "password": PassMan.hash(password.encode())})
            print("Your account has been created successfully")
            return successfulLoginResponse(forUsername=username)
        else:
            # it'd be nice if we had some sort of way to let the client know to display these errors. 
            # Perhaps there's somewhere we can inject these in the register/login html files
            print("Please edit the username")
    else:
        print("Please edit the password")

    return redirect("/")

def successfulLoginResponse(forUsername: str):
    authTokenSet: AuthTokenPair = AuthToken.newSet()
    authTokens.insert_one({
        "token":authTokenSet.hashed,
        "owner":forUsername,
        # use dateutil.parser.parse to turn this back into a date
        "timestamp":str(datetime.datetime.now())
    })
    
    response = make_response(redirect("/getstarted"))
    expirationDays = 30
    expSec = expirationDays * 24 * 60 * 60
    response.set_cookie('auth', authTokenSet.raw, max_age=expSec)
    return response

@app.route('/login/', methods=['POST'])
def insert_display_login():
    username = escape(request.form['username'])
    password = escape(request.form['psw'])

    proposedUser = users.find_one({"username":username})
    if proposedUser is None:
        print("No user exists for that username")
    else:
        hashedPassword = proposedUser["password"]
        result = PassMan.check(password.encode(), hashedPassword)
        # if password is correct, tell JS to send the user to the /getstarted
        # and store the cookie
        if result is True:
            return successfulLoginResponse(forUsername=proposedUser["username"])

    # otherwise, fall through to the normal login html
    response = make_response(createLoginPage(isLoggedIn=False, authToken=""))
    response.set_cookie("auth", "jk this is not that lol", max_age=0)
    return response


# This function will add cover image  in login and register pages
@app.route('/Login/Cover.png', methods=['GET'])
def getCoverImage():
    return open('./templates/Login/Cover.png', 'rb').read()

@app.route('/create.png', methods=['GET'])
def getCreateImage():
    return open('./templates/JoinCreate/create.png', 'rb').read(), 200, {'Content-Type': 'image/png'}

@app.route('/join.png', methods=['GET'])
def getJoinImage():
    return open('./templates/JoinCreate/join.png', 'rb').read(), 200, {'Content-Type': 'image/png'}

@app.route('/logo.png', methods=['GET'])
def getLogoImage():
    return open('./templates/logo.png', 'rb').read(), 200, {'Content-Type': 'image/png'}

@app.route('/msgIcon.png', methods=['GET'])
def getMsgIcon():
    return open('./templates/Workplace/msgIcon.png', 'rb').read(), 200, {'Content-Type': 'image/png'}

# Styles retrieval
@app.route("/styles/<stylesheet>/")
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
@app.route("/scripts/<scriptname>/")
def scriptRetrieval(scriptname):
    match scriptname:
        case "getstarted":
            content = open('./templates/JoinCreate/joincreate.js','rb').read()
        case "chat":
            content = open('./templates/Workplace/chat.js','rb').read()
    return content, 200, {'Content-Type':'text/js'}

@app.route("/myprofile", methods=['GET'])
def goToMyProfile():
    authToken = request.cookies.get("auth")
    if not AuthToken.validAuthToken(authCookie=authToken):
        return redirect("/")

    yourUsername = AuthToken.getUsernameFromAuthToken(authToken)
    return redirect(f"/user/{yourUsername}/")

@app.route("/user/<username>/", methods=['GET'])
def showProfile(username):
    # Need change: hardcode username, listNameCreate, ListNameJoin
    authToken = request.cookies.get("auth")
    if not AuthToken.validAuthToken(authCookie=authToken):
        return redirect("/")
    outerInjected = Templating.injectHTMLBody(srcFile="./templates/Profile/profile.html")
    withUsername= replacePlaceholder(outerInjected, "username", username)
    
    testuser = AuthToken.getUsernameFromAuthToken(authToken)
    if username == testuser:
        withType= replacePlaceholder(withUsername, "type", "submit")
    else:
        withType= replacePlaceholder(withUsername, "type", "hidden")

    userCreatedWorkspaces = workplaces.find({"userID":username})
    response = ""
    listUserCreatedWorkspaces = list(userCreatedWorkspaces)
    for wp in listUserCreatedWorkspaces:
        name: str = wp['workplace']
        code: str = wp['code']
        withName = replacePlaceholder(htmlElements.profileListedWorkspace, placeholder="workspaceName", newContent=name)
        withCode = replacePlaceholder(withName, placeholder="workspaceCode", newContent=code)
        if username == testuser:
            showVotes = replacePlaceholder(withCode, placeholder="hidden", newContent="display:visible")
            #Temporary implementation: newContent="0" must be updated to actual vote amount when total vote is implemented
            withVotes = replacePlaceholder(showVotes, placeholder="workspaceVotes", newContent="0")
        else:
            showVotes = replacePlaceholder(withCode, placeholder="hidden", newContent="display:none")
            withVotes = replacePlaceholder(showVotes, placeholder="workspaceVotes", newContent="0")
        response += withVotes

    allWorkplaces = workplaces.find()
    response2 = ""
    if allWorkplaces == None:
        return replacePlaceholder(withType, placeholder="listNameCreate",newContent=response)
    else:
        withCreated = replacePlaceholder(withType, placeholder="listNameCreate",newContent=response)
    for workplace in allWorkplaces:
            name2: str = workplace['workplace']
            code2: str = workplace['code']
            owner: str = workplace['userID']
            users = workplace.get('users')
            if users == None:
                return replacePlaceholder(withType, placeholder="listNameCreate",newContent=response)
            for user in users:
                if user == username and user != owner:
                    withName2 = replacePlaceholder(htmlElements.profileListedWorkspace, placeholder="workspaceName", newContent=name2)
                    withCode2 = replacePlaceholder(withName2, placeholder="workspaceCode", newContent=code2)
                    if user == testuser or owner == testuser:
                        showVotes2 = replacePlaceholder(withCode2, placeholder="hidden", newContent="display:visible")
                        #Temporary implementation: newContent="0" must be updated to actual vote amount when total vote is implemented
                        withVotes2 = replacePlaceholder(showVotes2, placeholder="workspaceVotes", newContent="0")
                    else:
                        showVotes2 = replacePlaceholder(withCode2, placeholder="hidden", newContent="display:none")
                        withVotes2 = replacePlaceholder(showVotes2, placeholder="workspaceVotes", newContent="0")
                    response2 += withVotes2

    return replacePlaceholder(withCreated, placeholder="ListNameJoin",newContent=response2)

@app.route("/changename/", methods=['POST'])
def update_name():
    authToken = request.cookies.get("auth")
    if not AuthToken.validAuthToken(authCookie=authToken):
        return redirect("/")
    userID = AuthToken.getUsernameFromAuthToken(authToken=authToken)
    newID = request.form['username']
    validUsername = verify.validate.verify_username(newID)
    newID = escape(newID)
    
    if validUsername:
        authTokens.update_many({'owner': userID}, {'$set': {'owner': newID}})
        workplaces.update_many({'userID': userID}, {'$set': {'userID': newID}})
        users.update_many({'username': userID}, {'$set': {'username': newID}})
        allWorkplaces = workplaces.find()
        for each in allWorkplaces:
            usersArr = each.get("users")
            code = each.get("code")
            x=0
            for x in range(len(usersArr)):
                if usersArr[x] == userID:
                    usersArr[x] = newID
                    break

            workplaces.update_one({'code': code}, {'$set': {'users': usersArr}})
        return redirect(url_for('showProfile',username=newID))
    else:
        print("invalid username")
        return redirect(url_for('showProfile',username=userID))

@app.route("/usercolor/<code>/", methods=['POST'])
def testusercolor(code):
    cookies = request.cookies
    color = request.form["color"]
    authToken = cookies.get("auth")
    user = AuthToken.getUsernameFromAuthToken(authToken=authToken)
    usercolor = user + "color"
    workplaces.update_one({"code": code}, {"$set": {usercolor: color}})
    return color

@app.route("/usercolor/<code>/", methods=['GET'])
def getusercolor(code):
    cookies = request.cookies
    authToken = cookies.get("auth")
    username = AuthToken.getUsernameFromAuthToken(authToken=authToken)
    workplace = workplaces.find({"code": code})
    for each in workplace:
        color = each.get(username+"color")
    
    if color == None:
        color = "None"
    return color

# WEBSOCKET STUFF

# when user joins room
@socketio.on('initialDataRequest')
def initialSend(data):
    authID = data['authToken']
    room = data['code']
    
    if not AuthToken.validAuthToken(authCookie=authID):
        socketio.emit('newMessage', {'messages': [makeMessage("[PRIVATE] SERVER",f"You are unauthorized. Your messages will not be sent. Please login first.", code=room)]}, to=request.sid)
        return
    else:
        username = AuthToken.getUsernameFromAuthToken(authID)
        join_room(room)
        broadcastNewMessage([makeMessage("SERVER", f"{username} entered the room.", room)], code=room)

        wp = workplaces.find_one({"code":room})
        question = wp.get("currentQuestion")
        timestamp = wp.get("questionExpiry")

        if timestamp is None:
            timestamp = datetime.datetime.fromtimestamp(1.0)
            print(timestamp)
        if question is None:
            question = "Waiting for question..."

        socketio.emit('dataDebrief', {'question':question,'timestamp':timestamp,'answers':"none"})


@socketio.on('message')
def handle_unnamed_message(message):
    print(f"handle_message: {str(message)}")
    escaped_message = escape(message)
    if "question_input" and "idea_input" in message:

        allegedAuth = request.cookies.get("auth")

        question_input = escaped_message.split(",")[0][19:-1]
        idea_input = escaped_message.split(",")[1][14:-1]
        workplace_code = escaped_message.split(",")[2][17:-1]
        # print(workplace_code)
        # print(escaped_message.split(",")[3][9:-2])
        user_color = escaped_message.split(",")[3][9:-2]

        


        wp = workplaces.find_one({"code":workplace_code})
        questionExpiry = wp.get("questionExpiry")
        if questionExpiry is not None:
            threshold = dateutil.parser.parse(questionExpiry)
        else:
            # if no questionExpiry available, just use the oldest timestamp available or whatever
            threshold = datetime.datetime.fromtimestamp(0.0)
        actual = datetime.datetime.now()
        if actual > threshold:
            print("regect answer for lateness")
            return
        else:
            print("allow") 

        if AuthToken.validAuthToken(allegedAuth):
            user = AuthToken.getUsernameFromAuthToken(allegedAuth)
            initial_answer = {"Submitted by": user, "Answer": idea_input, "Vote": str(0), "workplace_code": workplace_code}
            answerVotes.insert_one(initial_answer)

            initial_total_votes = {"User": user, "total_vote": str(0), "workplace_code": workplace_code}
            total_Vote_db = userTotalVotes.find_one({"User": user})

            if total_Vote_db is None:
                userTotalVotes.insert_one(initial_total_votes)
            else:
                print("User's total vote is in the database already")

        poll_message = {"question_input": question_input, "idea_input": idea_input, "workplace_code_1": workplace_code, "color": user_color}
        new_message_list = [poll_message]
        # print("poll_message:", poll_message)
        socketio.emit('poll_message', {'poll_message': poll_message}, to=workplace_code)

    elif "options_server" and "totalVotes_server" in escaped_message:

        poll_result = verify.process.process_result(escaped_message)

        wp = workplaces.find_one({"code":poll_result[2]})
        questionExpiry = wp.get("questionExpiry")
        if questionExpiry is not None:
            threshold = dateutil.parser.parse(questionExpiry)
        else:
            # if no questionExpiry available, just use the oldest timestamp available or whatever
            threshold = datetime.datetime.fromtimestamp(0.0)
        actual = datetime.datetime.now()
        if actual > threshold:
            print("regect answer for lateness")
            return
        else:
            print("allow") 

        result_message = {"options_server": poll_result[0], "total_votes_server": poll_result[1], "workplace_code_1": poll_result[2]}
        # print("result:", result_message)


        allegedAuth = request.cookies.get("auth")
        user = AuthToken.getUsernameFromAuthToken(allegedAuth)

        for x, y in poll_result[0].items():
            answer = {"Answer": x, "workplace_code": poll_result[2]}
            db_find = answerVotes.find_one(answer, {'_id': False})
            if db_find is None:
                print("Something wrong")
            else:
                new_content = {"Answer": x, "Vote": y, "workplace_code": poll_result[2]}
                # print("new_content", new_content)
                answerVotes.update_one(answer, {'$set': new_content})

        allUserDatabase = list(answerVotes.find({"workplace_code": poll_result[2]}, {'_id': False}))
        # allUserDatabase_2 = list(answerVotes.find({}, {'_id': False}))

        allTotalVoteDatabase = list(userTotalVotes.find({"workplace_code": poll_result[2]}, {'_id': False}))

        for x in allTotalVoteDatabase:
            username = x.get("User")
            total_vote = 0

            for y in allUserDatabase:
                if y.get("Submitted by") == username:
                    vote = y.get("Vote")
                    total_vote += int(vote)

            old_content = {"User": username, "total_vote": x.get("total_vote"), "workplace_code": x.get("workplace_code")}
            new_content = {"User": username, "total_vote": total_vote, "workplace_code": x.get("workplace_code")}

            userTotalVotes.update_one(old_content, {'$set': new_content})

        users_total_vote_test = list(userTotalVotes.find({"workplace_code": poll_result[2]}, {'_id': False}))
        answerVotes_test = list(answerVotes.find({"workplace_code": poll_result[2]}, {'_id': False}))
        print("users_total_vote_test", users_total_vote_test)
        print("answerVotes_test", answerVotes_test)


        socketio.emit('result_message', {'result_message': result_message}, to=poll_result[2])

        # print("options_server", options_server)
        # print("totalVotes_server", total_votes_server)
        # print("workplace_code", workplace_code)
    elif "allUsers" in escaped_message:
        allUsers = verify.process.process_users(escaped_message)[0]
        workspace_code = verify.process.process_users(escaped_message)[1]
        allVotes = verify.process.process_users(escaped_message)[2]
        result_message = {"allUsers": allUsers, "allVotes": allVotes}
        socketio.emit('allUsers', result_message, to=workspace_code)


    elif "updatedQuestion" in escaped_message:
        jsonformat = json.loads(escaped_message)

        print(jsonformat)
        workplaceCode = jsonformat["workplaceCode"]
        allegedAuth = request.cookies.get("auth")
        if AuthToken.validAuthToken(allegedAuth):
            user = AuthToken.getUsernameFromAuthToken(allegedAuth)
            
            workplace = workplaces.find_one({"code":workplaceCode})
            if user == workplace["userID"]:
                questionExpiry = jsonformat["questionExpirySeconds"]
                try:
                    floatSec = float(questionExpiry)
                    if floatSec is None:
                        return
                    timestamp = datetime.datetime.now() + datetime.timedelta(seconds=floatSec+1.0) # add 1.0 to account for processing delay
                    
                    question = jsonformat["updatedQuestion"]

                    workplaces.update_one({"code": workplaceCode},{"$set":{"currentQuestion":question, "questionExpiry":str(timestamp)}})
                    socketio.emit('updatedQuestion', {'updatedQuestion': question, "timestamp":str(timestamp)}, to=workplaceCode)
                except TypeError:
                    print("invalid time input")
                except ValueError:
                    print("invalid time input")

            else:
                print(f"A user by the name of {user} just tried to make an unauthenticated questionChange!!")
    else:
        
        print(f"handle_message: {str(message)}")
        newMessage = update_messages(json.loads(escaped_message))
        if newMessage != None:
            broadcastNewMessage(messages=[newMessage], code=newMessage["code"])

@socketio.on('json')
def handle_unnamed_json(json):
    print(f"handle_json: {str(json)}")
    print(type(json))

# broadcast to all clients for new message
def broadcastNewMessage(messages: list[dict], code: str):
    sendableMessages = map(lambda x: (json.loads(x)), messages)
    socketio.emit('newMessage', {'messages': messages}, to=code)

# moved to styleRetrieval method for coherency's sake
# @app.route("/profile.css", methods=['GET'])
# def profileCSS():
#     return open('./templates/Profile/profile.css', 'rb').read(), 200, {'Content-Type': 'text/css'}

# Site visible on http://127.0.0.1:8081/
if __name__ == "__main__":
    countStat = {"label": "viewCount"}
    countValue = {"value": 0}
    stats.update_one(countStat, {"$setOnInsert": countValue}, upsert=True)

    socketio.run(app,host="0.0.0.0", port=8081, debug=True)
