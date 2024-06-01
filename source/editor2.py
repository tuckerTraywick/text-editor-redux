import blessed
import blessed.terminal

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
		self.settings = {
			"relativeLineNumbers": True,
		}
		self.keybindings = {

		}
		self.colors = {

		}
		self.mode = "normal"
		self.keepRunning = True
		self.document = Document()
		# self.workingDirectory = ""

# Stores and presents the ui of the editor.
class EditorView:
	def __init__(self, model):
		self.model = model
		self.printer = Printer()
		self.statusLineLeft = ""
		self.statusLineRight = ""
		# self.message = ""
		# self.command = None
		# self.findTerm = None
		# self.replaceTerm = None
		# self.browserFileList = None

# Represents a buffer along with it's cursor. Used to manipulate text.
class Document:
	def __init__(self):
		self.buffer = Buffer()
		self.cursor = Cursor()
		self.file = None
		self.name = ""

# Stores and manipulates the lines of a file to be edited.
class Buffer:
	def __init__(self):
		self.lines = []

# Stores the position of the text cursor.
class Cursor:
	def __init__(self):
		self.y = 0
		self.x = 0

# Does buffered output to the terminal. Used by `EditorView` to prevent flickering.
class Printer:
	def __init__(self):
		self.terminal = blessed.Terminal()
		self.output = ""
