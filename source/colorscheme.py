# Represents a colorscheme for the editor and syntax highlighting.
class Colorscheme:
	def __init__(self):
		self.name = "default dark"
		self.colors = {

		}
		self.tokens = {
			"keyword": {
				"for", "return",
			},
			"symbol": "~`!@#$%^&*()_-+=\\|,<.>/?",
		}
		self.pairs = {
			"parenthesis": ("(", ")"),
			"brackets": ("[", "]"),
			"braces": ("{", "}"),
			"lineComment": ("//", "\n")
		}

	# Applies syntax highlighting to a line.
	def highlight(self, line):
		i = 0
		token = ""
		result = ""

		# Break the line into tokens and append each token to the result with highlighting.
		while i < len(line):
			# Skip spaces.
			if line[i].isspace():
				result += line[i]
				i += 1
			# Highlight an identifier or keyword.
			elif line[i].isalpha() or line[i] == "_":
				# Get the identifier.
				while i < len(line) and (line[i].isalnum() or line[i] == "_"):
					token += line[i]
					i += 1
				
				# If it's a keyword, highlight it as such.
				if token in self.keywords:
					result += self.colors["keyword"](token)
				else:
					result += self.colors["identifier"](token)
				token = ""
			# Highlight a number.
			elif line[i].isdigit():
				while i < len(line) and line[i].isdigit():
					token += line[i]
					i += 1
				result += self.colors["number"](token)
				token = ""
			# Higlight a symbol.
			elif line[i] in self.symbols:
				while i < len(line) and line[i] in self.symbols:
					token += line[i]
					i += 1
				result += self.colors["symbol"](token)
				token = ""
			# Highlight a string.
			elif line[i] == '"':
				token += line[i]
				i += 1

				while True:
					if i >= len(line):
						break
					elif line[i] == '"':
						token += line[i]
						i += 1
						break
					else:
						token += line[i]
						i += 1
				result += self.colors["string"](token)
				token = ""
			# Highlight a line comment.
			elif line[i] == self.lineComment:
				result += self.colors["lineComment"](line[i:])
				break
			# Apply default highlighting.
			else:
				result += line[i]
				i += 1

		return result
