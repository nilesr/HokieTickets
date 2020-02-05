#!/usr/bin/env python2
import sqlite3, os, base64, cookies, pickle
import libgoblin

def connect():
	return sqlite3.connect("/dev/shm/goblin.db")

db = connect()
cur = db.cursor()
cur.execute("create table if not exists sessions (user text, cookie text, session blob);")
cur.close()
db.commit()
del db

#########################################################
## Restart mako-server every time you change this file ##
#########################################################

class Session:
	def __init__(self, b, c, u):
		self._db = connect()
		self._backing_dict = b
		self._cookie = c
		self._user = u
		self._cur = self._db.cursor()
	def __getitem__(self, k):
		return self._backing_dict[k]
	def __setitem__(self, k, v):
		self._backing_dict[k] = v
		self._cur.execute("update sessions set session = ? where user = ? and cookie = ?", [pickle.dumps(self._backing_dict), self._user, self._cookie])
		self._db.commit()
	def __str__(self):
		return str(self._backing_dict)
	def __repr__(self):
		return repr(self._backing_dict)

def try_login(d, environ):
	if "user" not in d or "pass" not in d:
		return False, False
	try:
		libgoblin.get_user_info(d["user"])
	except Exception, e:
		return False, "User does not exist"
	if d["pass"] != "pass":
		return False, "Invalid password"
	if not libgoblin.check_permissions_grant(d["user"]):
		return False, "Permissions grant check failed - the hokipoki account does not have permission to perform eosio.token actions on your behalf."
	db = connect()
	cur = db.cursor()
	cur.execute("delete from sessions where user = ?", [d["user"]])
	cookie = base64.b64encode(os.urandom(35)).decode("ascii")
	cur.execute("insert into sessions (user, cookie, session) values (?, ?, ?)", [d["user"], cookie, pickle.dumps({})])
	environ["headers"] = [("Set-Cookie", cookies.Cookie("auth", cookie).render_response())]
	db.commit()
	cur.close()
	return d["user"], Session({}, cookie, d["user"])

def get_user(c):
	if "auth" not in c:
		return False, False
	db = connect()
	cur = db.cursor()
	cur.execute("select user, session from sessions where cookie = ?", [c["auth"]])
	r = cur.fetchone()
	if not r:
		cur.close()
		return False, False
	return r[0], Session(pickle.loads(r[1]), c["auth"], r[0])
	cur.close()

def destroy_session(c):
	if "auth" not in c:
		return False
	db = connect()
	cur = db.cursor()
	cur.execute("delete from sessions where cookie = ?", [c["auth"]])
	if cur.rowcount == 0:
		cur.close()
		return False
	db.commit()
	cur.close()
	return True

