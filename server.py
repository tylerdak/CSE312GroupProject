from flask import Flask
from numpy import place
import pymongo
import json

app = Flask(__name__)

def escape(htmlStr):
    return htmlStr.replace("&","&amp").replace("<","&lt").replace(">","&gt")

def replacePlaceholder(oldText: str, placeholder: str, newContent: str):
    return oldText.replace("{{" + placeholder + "}}", newContent)


# Add viewCount retrieval code here
#
# I've added code to replace placeholders with whatever
# you end up returning in this function (ideally a correct
# page count)
def getCurrentPageViewCount():
    return 0

@app.route("/")
def index():
    with open("index.html") as f:
        return replacePlaceholder(
            oldText=f.read(), 
            placeholder="placeholder",
            newContent=f"Page Count: {str(getCurrentPageViewCount())}"
        )

@app.route("/<string:query>")
def queriedPage(query):
    query = escape(query)
    with open("index.html") as f:
        return replacePlaceholder(
            oldText=f.read(), 
            placeholder="placeholder",
            newContent=f"Sitewide View Count: {str(getCurrentPageViewCount())}<br>Your Query: {query}"
        )