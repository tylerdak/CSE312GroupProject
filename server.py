from flask import Flask, request
# from numpy import place
# import pymongo
from pymongo import MongoClient
import json

app = Flask(__name__)

# client = MongoClient("mongodb+srv://cse312group:db@cluster0.u70wkht.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient("mongo")
db = client["CSE312Group"]
stats = db["stats"]

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
    return stats.find_one({"label":"viewCount"})['value']
    
def incrementPageViewCount():
    counter = getCurrentPageViewCount()
    stats.update_one({"label":"viewCount"}, {"$set": {"value": counter+1}})
    return counter+1

@app.route("/")
def index():
    incrementPageViewCount()
    with open("index.html") as f:
        return replacePlaceholder(
            oldText=f.read(), 
            placeholder="count",
            newContent=f"Page Count: {str(getCurrentPageViewCount())}"
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

# Site visible on http://127.0.0.1:5000/
if __name__ == "__main__":
    countStat = {"label":"viewCount"}
    countValue = {"value":0}
    stats.update_one(countStat,{"$setOnInsert": countValue}, upsert=True)
    app.run(host="0.0.0.0", port=8081, debug=True)
