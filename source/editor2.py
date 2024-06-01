import blessed

# Handles the logic and main loop for the editor.
class EditorController:
	def __init__(self):
		self.model = EditorModel()
		self.view = EditorView()

	def processKeypress(self, key):
		if key in self.model.keybindings:
			binding = self.model.keybindings[self.model.mode][key]
			binding(key)
		elif "else" in self.model.keybindings:
			binding = self.model.keybindings[self.model.mode]["else"]
			binding(key)

	def run(self):
		while self.model.keepRunning:
			self.view.draw(self.model)
			key = self.view.getKeypress()
			self.processKeypress(key)

# Stores and manipulates the state of the editor.
class EditorModel:
	def __init__(self):
		self.settings = {}
		self.keybindings = {}
		self.mode = "normal"
		self.keepRunning = True
		self.document = None

# Stores and presents the ui of the editor.
class EditorView:
	def __init__(self, model):
		self.model = model
		self.statusLineLeft = ""
		self.statusLineRight = ""
		self.message = ""
		self.command = None
		self.findTerm = None
		self.replaceTerm = None
		self.browserFindTerm = None
		self.browserFileList = None

class Document:
	pass

class Buffer:
	pass

class Cursor:
	pass
