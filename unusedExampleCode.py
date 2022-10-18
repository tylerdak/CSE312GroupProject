from templating import *


def pretendReplaceFunction():
	result = "True"
	newLogin = Templating.injectHTMLBody(None,srcFile="templates/Login.html")

	comments = ["Comment 1", "comment 2"]
	iteratedData = ""
	for comment in comments:
		iteratedData += f"<h2>{comment}</h2>\n"

	return Templating.replacePlaceholder(oldText=newLogin,placeholder="data",newContent=iteratedData)