import flask
from flask import Flask, request, redirect
from pymongo import MongoClient
# import json
# from numpy import place
# import pymongo

app = Flask(__name__)

# client = MongoClient("mongodb+srv://cse312group:db@cluster0.u70wkht.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient("mongo")
db = client["CSE312Group"]
stats = db["stats"]
users = db["users"]


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
    all_users = list(users.find({}, {'email': 1, '_id': 0}))
    all_users_list = []
    for x in all_users:
        email_insert = "Email: ", x.get("email")
        all_users_list.insert(0, email_insert)

    incrementPageViewCount()
    return flask.render_template("index.html",
                                 count=f"Page Count: {str(getCurrentPageViewCount())}",
                                 users=all_users_list
                                 )


@app.route("/<string:query>")
def queriedPage(query):
    query = escape(query)
    with open("templates/index.html") as f:
        return replacePlaceholder(
            oldText=f.read(),
            placeholder="count",
            newContent=f"Sitewide View Count: {str(getCurrentPageViewCount())}<br>Your Query: {query}"
        )


# This function will redirect the page to the main page after submitting the form, otherwise it will give the error
# "Method not allowed for requested URL"
@app.route('/', methods=['POST'])
def insert_display():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['psw']
        users.insert_one({"email": email, "password": password})
        return redirect("http://127.0.0.1:8081", code=302)
    else:
        return "Error"


# Site visible on http://127.0.0.1:5000/
if __name__ == "__main__":
    countStat = {"label": "viewCount"}
    countValue = {"value": 0}
    stats.update_one(countStat, {"$setOnInsert": countValue}, upsert=True)
    app.run(host="0.0.0.0", port=8081, debug=True)
