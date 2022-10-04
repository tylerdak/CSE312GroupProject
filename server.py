from flask import Flask
from numpy import place
import pymongo
import json
from json import load, dump
from pymongo import MongoClient

app = Flask(__name__)

clients = []
mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
users_collection = db["users"]
user_id_collection = db["user_id"]


def escape(htmlStr):
    return htmlStr.replace("&", "&amp").replace("<", "&lt").replace(">", "&gt")


def replacePlaceholder(oldText: str, placeholder: str, newContent: str):
    return oldText.replace("{{" + placeholder + "}}", newContent)


# Add viewCount retrieval code here
#
# I've added code to replace placeholders with whatever
# you end up returning in this function (ideally a correct
# page count)
# I am using a different implementation for view count
def getCurrentPageViewCount():

    return 0


@app.route("/")
def index():
    with open("View.json") as g:
        view = load(g) + 1
        with open("View.json", "w") as f:
            dump(view, f)

    with open("index.html") as f:
        return replacePlaceholder(
            oldText=f.read(),
            placeholder="count",
            newContent=f"Page Count: {str(view)}"
        )


@app.route("/<string:query>")
def queriedPage(query):
    query = escape(query)
    with open("index.html") as f:
        return replacePlaceholder(
            oldText=f.read(),
            placeholder="count",
            newContent=f"Sitewide View Count: {str(getCurrentPageViewCount())}<br>Your Query: {query}"
        )


if __name__ == "__main__":
    app.run()