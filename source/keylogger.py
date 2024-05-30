import blessed

term = blessed.Terminal()
with term.cbreak():
	while True:
		key = term.inkey()
		if key == "q":
			break
		print(key, key.name, key.is_sequence, end="\r\n")
