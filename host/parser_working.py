import random
import re

inputReg = re.compile(r'^([0-9d\+\-\*\/\\\s\,]+)$', re.IGNORECASE)
multiplierReg = re.compile(r'^([0-9]+)\s(.*)$', re.IGNORECASE)
modifierReg = re.compile(r'^(.*)([+|-]\s?[0-9]+)$', re.IGNORECASE)

def parseQuery (text):
	multiplierMatch = re.match(multiplierReg, text)
	if multiplierMatch:
		multiplier = int(multiplierMatch.group(1))
		text = multiplierMatch.group(2)
	else:
		multiplier = 1

	modifierMatch = re.match(modifierReg, text)
	if modifierMatch:
		modifier = int(modifierMatch.group(2).replace(' ', ''))
		text = modifierMatch.group(1).strip()
	else:
		modifier = 0

	if len(text.split('d')) == 2:
		count, amount = text.split('d')

		if amount.isdecimal():
			amount = int(amount)
		elif len(amount) == 0:
			amount = 20
		else:
			return None

		if count.isdecimal():
			count = int(count)
		elif len(count) == 0:
			count = 1
		else:
			return None

		return {
			'repetitions': multiplier,
			'diceTotal': count,
			'diceSection': None,
			'rangeStart': min(amount, 1),
			'rangeStop': amount + 1,
			'modifier': modifier
		}
	else:
		return None

def runQuery (query):
	return [
		sum([
			random.randrange(query['rangeStart'], query['rangeStop'])
			for j in range(query['diceTotal'])
		]) + query['modifier']
		for i in range(query['repetitions'])
	]

def getRoll (message):
	inputMatch = re.match(inputReg, message)
	if inputMatch:
		queries = [parseQuery(i.strip()) for i in inputMatch.group(1).split(',')]
		values = [runQuery(i) for i in queries]
		out = ' and '.join([
			', '.join(str(j) for j in i)
			for i in values
		])
		return out