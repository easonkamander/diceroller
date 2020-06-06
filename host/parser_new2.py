import re

reValidExpDie = re.compile(r"^[0-9d\<\>]+$", re.IGNORECASE)
reValidExp2 = re.compile(r"^[0-9d\<\>\^]+$", re.IGNORECASE)
reValidExp1 = re.compile(r"^[0-9d\<\>\^\*\/]+$", re.IGNORECASE)
reValidExp0 = re.compile(r"^[0-9d\<\>\^\*\/\+\-]+$", re.IGNORECASE)

def splitBinary (text, brk0, brk1):
	if text.startswith(brk0):
		sign = False
		text = text[len(brk0):]
	elif text.startswith(brk1):
		sign = True
		text = text[len(brk1):]
	else:
		sign = True
	if brk0 in text and brk1 in text:
		return [(sign, text[:min(text.index(brk0), text.index(brk1))])] + splitBinary(text[min(text.index(brk0), text.index(brk1)):], brk0, brk1)
	elif brk0 in text:
		return [(sign, text[:text.index(brk0)])] + splitBinary(text[text.index(brk0):], brk0, brk1)
	elif brk1 in text:
		return [(sign, text[:text.index(brk1)])] + splitBinary(text[text.index(brk1):], brk0, brk1)
	else:
		return [(sign, text)]

class Exp:
	def __init__ (self, text):
		if re.match(reValidExpDie, text):
			pass # parsed as obj
		elif re.match(reValidExp2, text):
			pass # parsed as obj
		elif re.match(reValidExp1, text):
			pass # parsed as obj
		elif re.match(reValidExp0, text):
			pass # parsed as obj
		elif len(text):
			pass # throw invalid character exception
		else:
			pass # throw empty expression exception

print(splitBinary('abc+def-ghi-ery+q+z', '-', '+'))