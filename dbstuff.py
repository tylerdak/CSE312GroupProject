from pymongo import MongoClient

client = MongoClient("mongo")
db = client["CSE312Group"]
stats = db["stats"]
users = db["users"]
workplaces = db["workplaces"]
authTokens = db["authTokens"]
answerVotes = db["answerVotes"]
userTotalVotes = db["userTotalVotes"]
