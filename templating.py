from bs4 import BeautifulSoup

class Templating:

	def injectHTMLBody(srcFile: str, templateFile: str = "/templates/outer.html"):
		with open(srcFile, 'r') as src:
			src = src.read()
			print(src)

			soup = BeautifulSoup(html, "html.parser")