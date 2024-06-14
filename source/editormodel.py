from document import Document

# Converts a key + control (ex. "^A") to it's ASCII representation.
def ctrl(char):
	return chr(ord(char.upper()) - 64)

# Stores and manipulates the state of the editor.
class EditorModel:
	def __init__(self, controller):
		self.settings = {
			"relativeLineNumbers": True,
		}
		self.keybindings = {
			"normal": {
				"j": self.cursorLeftCharacter,
				"l": self.cursorRightCharacter,
				"i": self.cursorUpLine,
				"k": self.cursorDownLine,
				"J": self.cursorLeftWord,
				"L": self.cursorRightWord,
				"I": self.cursorUpPage,
				"K": self.cursorDownPage,
				ctrl("j"): self.cursorLeftWORD,
				ctrl("l"): self.cursorRightWORD,
				ctrl("i"): self.cursorUpPAGE,
				ctrl("k"): self.cursorDownPAGE,
				" ": self.enterInsertMode,
				ctrl("c"): self.quit,
				ctrl("s"): self.save,
				"KEY_UP": self.cursorUpLine,
				"KEY_DOWN": self.cursorDownLine,
				"KEY_LEFT": self.cursorLeftCharacter,
				"KEY_RIGHT": self.cursorRightCharacter,
				# "KEY_ENTER": self.splitLine,
				"KEY_BACKSPACE": self.deleteCharacterLeft,
				"KEY_DELETE": self.deleteCharacterRight,
			},
			"insert": {
				ctrl("c"): self.quit,
				"KEY_ESCAPE": self.enterNormalMode,
				"KEY_UP": self.cursorUpLine,
				"KEY_DOWN": self.cursorDownLine,
				"KEY_LEFT": self.cursorLeftCharacter,
				"KEY_RIGHT": self.cursorRightCharacter,
				"KEY_ENTER": self.splitLine,
				"KEY_BACKSPACE": self.deleteCharacterLeft,
				"KEY_DELETE": self.deleteCharacterRight,
				"else": self.insert,
			},
		}
		self.mode = "normal"
		self.keepRunning = True
		self.document = Document()

	###############################
	#### KEYBINDING FUNCTIONS #####
	###############################
	# Closes the file being edited and stops the editor.
	def quit(self, key):
		self.document.close()
		self.keepRunning = False

	# Saves the model.document to the file.
	def save(self, key):
		self.document.save()

	# Moves the cursor up a line.
	def cursorUpLine(self, key):
		self.document.cursorUpLine()
		
	# Moves the cursor down a line.
	def cursorDownLine(self, key):
		self.document.cursorDownLine()
		
	# Moves the left a character.
	def cursorLeftCharacter(self, key):
		self.document.cursorLeftCharacter()

	# Moves the cursor up a line.
	def cursorRightCharacter(self, key):
		self.document.cursorRightCharacter()
		
	# Moves the cursor left a word.
	def cursorLeftWord(self, key):
		self.document.cursorLeftWord()
		
	# Moves the cursor right a word.
	def cursorRightWord(self, key):
		self.document.cursorRightWord()
		
	# Moves the cursor left a big word.
	def cursorLeftWORD(self, key):
		self.document.cursorLeftWORD()
		
	# Moves the cursor right a big word.
	def cursorRightWORD(self, key):
		self.document.cursorRightWORD()
		
	# Inserts a character at the cursor.
	def insert(self, key):
		if key.isprintable():
			self.document.insert(key)
			
	# Splits the current line at the cursor.
	def splitLine(self, key):
		self.document.splitLine()
		
	# Joins the current line with the previous line.
	def joinPreviousLine(self, key):
		self.document.joinPreviousLine()
		
	# Deletes a character to the left of the cursor.
	def deleteCharacterLeft(self, key):
		self.document.deleteCharacterLeft()

	# Deletes a character to the right of the cursor.
	def deleteCharacterRight(self, key):
		self.document.deleteCharacterRight()
		
	# Returns back to normal mode.
	def enterNormalMode(self, key):
		self.mode = "normal"
		
	# Enters insert mode.
	def enterInsertMode(self, key):
		self.mode = "insert"
		
	# Moves the cursor up one half of the screen.
	def cursorUpPage(self, key):
		self.document.cursorUpPage()
		
	# Moves the cursor down one half of the screen.
	def cursorDownPage(self, key):
		self.document.cursorDownPage()

	# Moves the cursor up a whole screen.
	def cursorUpPAGE(self, key):
		self.document.cursorUpPAGE()
		
	# Moves the cursor down a whole screen.
	def cursorDownPAGE(self, key):
		self.document.cursorDownPAGE()
