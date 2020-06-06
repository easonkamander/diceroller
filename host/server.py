#!/usr/bin/python3 -u
import asyncio
import websockets
import json
import random
import parser
import time
import re
import urllib

PING_INTERVAL = 1

reValidName = re.compile(r"^[\w ]+$", re.IGNORECASE)

groups = {'': None}
users = {'': None}

class Group:
	def __init__ (self, user):
		self.key = ''
		while self.key in groups:
			self.key = '%008x' % random.randrange(16**8)
		groups[self.key] = self
		self.name = None
		self.users = [user]

	async def send (self, msg):
		await asyncio.wait([u.send({'order': 'group', **msg}) for u in self.users])

	def getList (self):
		return [(u.name, u.pingStt) for u in self.users]

class User:
	def __init__ (self):
		self.key = ''
		while self.key in users:
			self.key = '%016x' % random.randrange(16**16)
		users[self.key] = self
		self.cnx = None
		self.name = None
		self.group = None
		self.pingTime = time.time()
		self.pingStt = 1
		self.pingTsk = None

	def setCnx (self, cnx):
		if self.cnx:
			self.cnx.close()
		self.cnx = cnx

	async def send (self, msg):
		if self.cnx:
			await self.cnx.send(msg)

	async def receive (self, msg):
		if self.group and self.pingStt > 0:
			self.pingStt = 0
			await self.group.send({'list': self.group.getList()})
		if 'order' in msg and msg['order'] == 'group':
			if 'name' in msg and self.group is not None and self.group.users[0] is self and re.match(reValidName, msg['name']):
				self.group.name = msg['name']
				await self.group.send({'name': self.group.name})
			if 'crt' in msg and self.group is None:
				self.group = Group(self)
				await self.group.send({'crt': self.group.key, 'name': self.group.name, 'list': self.group.getList()})
			if 'att' in msg and self.group is None:
				if len(msg['att']) and msg['att'] in groups:
					self.group = groups[msg['att']]
					self.group.users.append(self)
					await self.send({'order': 'group', 'att': self.group.key, 'name': self.group.name, 'list': self.group.getList()})
					await self.group.send({'list': self.group.getList()})
				else:
					await self.send({'att': False})
			if 'rmv' in msg and self.group is not None:
				if self.group.users[0] is self:
					del groups[self.group.key]
					await self.group.send({'rmv': True})
					for u in self.group.users[::-1]:
						u.group = None
				else:
					self.group.users.remove(self)
					await self.group.send({'list': self.group.getList()})
					self.group = None
					await self.send({'order': 'group', 'rmv': True})
			if 'qry' in msg and self.group is not None:
				await self.group.send({'qry': {
					'name': self.name,
					'req': msg['qry'],
					'res': parser.getRoll(msg['qry'])
				}})
		else:
			if 'ping' in msg:
				asyncio.create_task(self.ping())
			if 'name' in msg and re.match(reValidName, msg['name']):
				self.name = msg['name']
				await self.send({'name': self.name})
				if self.group is not None:
					await self.group.send({'list': self.group.getList()})

	async def ping (self):
		if self.pingTsk is not None:
			self.pingTsk.cancel()
		delta, self.pingTime = max(0, self.pingTime + PING_INTERVAL - time.time()), time.time()
		await asyncio.sleep(delta)
		await self.send({'ping': True})
		self.pingTsk = asyncio.create_task(self.pingTmt())

	async def pingTmt (self):
		await asyncio.sleep(2)
		self.pingStt = 1
		if self.group:
			await self.group.send({'list': self.group.getList()})
		await asyncio.sleep(4)
		self.pingStt = 2
		if self.group:
			await self.group.send({'list': self.group.getList()})
		if self.cnx is not None:
			self.cnx.close()
			self.setCnx(None)

class Cnx:
	def __init__(self, skt, path):
		self.skt = skt
		pathOpt = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(path).query))
		if 'user' in pathOpt and len(pathOpt['user']) and pathOpt['user'] in users:
			self.user = users[pathOpt['user']]
		else:
			self.user = User()
		self.user.setCnx(self)

	async def send (self, msg):
		await self.skt.send(json.dumps(msg))

	async def receive (self, msg):
		await self.user.receive(msg)

	def close (self):
		if self.skt is not None:
			self.skt.close()
		self.skt = None
		self.user = None

async def main (skt, path):
	cnx = Cnx(skt, path)
	await cnx.send({'key': cnx.user.key})
	await cnx.send({'ping': True})
	try:
		async for msg in skt:
			await cnx.receive(json.loads(msg))
	finally:
		print('x')

start_server = websockets.serve(main, "localhost", 8021)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()