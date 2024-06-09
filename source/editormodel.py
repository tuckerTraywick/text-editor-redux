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
				"j": controller.cursorLeftCharacter,
				"l": controller.cursorRightCharacter,
				"i": controller.cursorUpLine,
				"k": controller.cursorDownLine,
				"J": controller.cursorLeftWord,
				"L": controller.cursorRightWord,
				"I": controller.cursorUpPage,
				"K": controller.cursorDownPage,
				ctrl("j"): controller.cursorLeftWORD,
				ctrl("l"): controller.cursorRightWORD,
				ctrl("i"): controller.cursorUpPAGE,
				ctrl("k"): controller.cursorDownPAGE,
				" ": controller.enterInsertMode,
				ctrl("c"): controller.quit,
				ctrl("s"): controller.save,
				"KEY_UP": controller.cursorUpLine,
				"KEY_DOWN": controller.cursorDownLine,
				"KEY_LEFT": controller.cursorLeftCharacter,
				"KEY_RIGHT": controller.cursorRightCharacter,
				# "KEY_ENTER": controller.splitLine,
				"KEY_BACKSPACE": controller.deleteCharacterLeft,
				"KEY_DELETE": controller.deleteCharacterRight,
			},
			"insert": {
				ctrl("c"): controller.quit,
				"KEY_ESCAPE": controller.enterNormalMode,
				"KEY_UP": controller.cursorUpLine,
				"KEY_DOWN": controller.cursorDownLine,
				"KEY_LEFT": controller.cursorLeftCharacter,
				"KEY_RIGHT": controller.cursorRightCharacter,
				"KEY_ENTER": controller.splitLine,
				"KEY_BACKSPACE": controller.deleteCharacterLeft,
				"KEY_DELETE": controller.deleteCharacterRight,
				"else": controller.insert,
			},
		}
		self.mode = "normal"
		self.keepRunning = True
		self.document = Document()
