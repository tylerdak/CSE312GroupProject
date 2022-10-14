from bs4 import BeautifulSoup, ResultSet

class Templating:

	defaultShellTemplate = "templates/outer.html"

	def replacePlaceholder(oldText: str, placeholder: str, newContent: str):
		# sourcery skip: instance-method-first-arg-name
		# ^^ don't worry about this

		return oldText.replace("{{" + placeholder + "}}", newContent)

	def injectHTMLBody(self=None,srcFile: str=None, templateFile: str = defaultShellTemplate):

		with open(templateFile, 'r') as dst:
			dst = dst.read()

		if srcFile is None:
			return templateFile.read()

		with open(srcFile, 'r') as src:
			src = src.read()

		soup = BeautifulSoup(src, "html.parser")

		toBeInjected: ResultSet = soup.find_all('body')
		toBeInjected = toBeInjected[0]

		return Templating.replacePlaceholder(oldText=dst, placeholder="body", newContent=str(toBeInjected))

	