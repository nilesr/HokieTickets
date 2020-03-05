#!/usr/bin/env python2
import json, subprocess, collections, random, datetime
cleos = ["cleos", "--no-auto-keosd", "-u", "http://127.0.0.1:8888", "--wallet-url", "unix:///home/ubuntu/eosio-wallet/keosd.sock"]
KEY = "EOS7J1tYpCHkCCvi5DwYXkJMRKRzK9XAUVvMC7PnrcucNXS6ZuMC1"
KEYWORDS = {"from", "except", "if", "else", "elif", "return"}


#########################################################
## Restart mako-server every time you change this file ##
#########################################################

class EosioError(Exception):
    # TODO - more post-processing, parse out exact error message, etc...
    def __init__(self, output):
	self.output = output

def _try_symbolize_names(l):
	if isinstance(l, list): return [_try_symbolize_names(i) for i in l]
	if not isinstance(l, dict): return l
	l = {k if k not in KEYWORDS else k + "_": _try_symbolize_names(v) for k, v in l.items()} # recurse
	cls = collections.namedtuple("t", l.keys())
	old_getitem = cls.__getitem__
	cls.__getitem__ = lambda self, k: l[k] if isinstance(k, str) else old_getitem(self, k)
	return cls(**l)

def _exec(l, json_decode = True):
	if not isinstance(l, list): raise TypeError("Invalid object passed to libgoblin._exec(): {}".format(str))
	proc = subprocess.Popen(cleos + l, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()
	stdout = stdout.decode("utf-8")
	stderr = stderr.decode("utf-8")
	if proc.returncode != 0:
		raise EosioError(stderr)
	if json_decode:
		return _try_symbolize_names(json.loads(stdout))
	return stdout

def get_info():
	return _exec(["get", "info"])

def get_user_info(user):
	return _exec(["get", "account", "-j", user])

def check_permissions_grant(user):
	ui = get_user_info(user)
	ps = [x for x in ui.permissions if x.perm_name == "active"]
	if len(ps) != 1: return False
	return any(f.permission.actor == "hokipoki" and f.permission.permission == "eosio.code" for f in ps[0].required_auth.accounts)


def get_balance(user):
	bal = _exec(["get", "currency", "balance", "eosio.token", user, "HTK"], False)
	bal = bal.strip()
	# if they have never had any HTK it prints an empty string
	if len(bal) == 0:
		return 0
	# bal looks like "1000000000.00 HTK"
	return float(bal.split()[0])

def get_currency_stats():
	return _exec(["get", "currency", "stats", "eosio.token", "HTK"]).HTK

def format_htk(c):
	return "{:,.2f}".format(float(str(c).split()[0])) + " HTK"

def get_raw_table(table):
	return _exec(["get", "table", "hokipoki", "hokipoki", table, "-l", "-1"]).rows

def get_declared_tables():
	return [t.name for t in _exec(["get", "abi", "hokipoki"]).tables]

def create_account(user):
	_exec(["create", "account", "eosio", user, KEY], False)
	_exec(["set", "account", "permission", user, "active",
		'{"threshold":1, "keys":[{"key":"'+KEY+'", "weight":1}], "accounts": [{"permission":{"actor":"hokipoki","permission":"eosio.code"},"weight":1}]}',
		"owner", "-p", user], False)
	_exec(["push", "action", "hokipoki", "adduser", json.dumps([user]), "-p", "hokipoki@active"], False)

# For debugging only. Put the output of debug_format() in a <pre> tag, or on the console
def _debug_is_complex(t):
	return (isinstance(t, tuple) and type(t) != tuple) or isinstance(t, list) or "\n" in str(t)
def debug_format(t, depth=0, dash=False):
	pad = "    " * depth
	firstpad = pad[:-2] + "- " if dash else pad
	if isinstance(t, tuple) and type(t) != tuple:
		l = [k + ":" + ("\n" + debug_format(v, depth+1, False) if _debug_is_complex(v) else " " + str(v)) for k, v in t.__dict__.items()]
		return "\n".join([(firstpad if i == 0 else pad) + x for i, x in enumerate(l)])
	if isinstance(t, list):
		return "\n".join([debug_format(x, depth+1, True) for x in t])
	return firstpad + str(t)


#TODO: make it return formatted output
# USER ACTIONS
def buy(user, game_id):
	parsed = get_raw_table("tickets")
	ticket_id = -1
	filtered = filter(lambda a:a["game_id"]==game_id and a["for_lottery"]==0 and a["owner"]=="hokipoki",parsed)
	if len(filtered) > 0:
		ticket_id= filtered[0]["id"]
	#TODO: Error if ticket is not available
	try:
		_exec(["push", "action", "hokipoki", "buy", json.dumps([user, ticket_id]), "-p", user + "@active", "-j"])
		return get_balance(user)
	except EosioError as e:
		return e.output


def sell(user, ticket_id):
	return _exec(["push", "action", "hokipoki", "sell", json.dumps([user, ticket_id]), "-p", user + "@active", "-j"])

def enter_lottery(user, game_id):
	r1 = random.randint(0, 2 ** 64 - 1)
	r2 = random.randint(0, 2 ** 64 - 1)
	r3 = random.randint(0, 2 ** 64 - 1)
	r4 = random.randint(0, 2 ** 64 - 1)
	return _exec(["push", "action", "hokipoki", "enterlottery", json.dumps([user, game_id, r1, r2, r3, r4]), "-p", user + "@active", "-j"])

def leave_lottery(user, game_id):
	return _exec(["push", "action", "hokipoki", "leavelottery", json.dumps([user, game_id]), "-p", user + "@active", "-j"])


# ADMIN ACTIONS
def execute_lottery(game_id):
	return _exec(["push", "action", "hokipoki", "executelotto", json.dumps([game_id]), "-p", "hokipoki@active", "-j"])

def open_lottery(game_id):
	return _exec(["push", "action", "hokipoki", "openlottery", json.dumps([game_id]), "-p", "hokipoki@active", "-j"])

def create_game(day, num_tickets, tickets_for_lotto, price, name, location, lottery_opens, lottery_closes):
	return _exec(["push", "action", "hokipoki", "creategame", json.dumps([day, num_tickets, tickets_for_lotto, price, name, location, lottery_opens, lottery_closes]), "-p", "hokipoki@active", "-j"])

def reset():
	return _exec(["push", "action", "hokipoki", "reset", json.dumps([]), "-p", "hokipoki@active"])


# USER AND ADMIN ACTIONS
def tickets():
	return _exec(["get", "table", "hokipoki", "hokipoki", "tickets", "-l", "-1"])

def games():
	return _exec(["get", "table", "hokipoki", "hokipoki", "games", "-l", "-1"])

def lottery_entries():
	return _exec(["get", "table", "hokipoki", "lottoentries", "-l", "-1"])

#REQUESTS RECIEVED FROM RACHEL

#returns all tickets that a user owns
def user_tickets(user):
	return filter(lambda a:a["owner"]==user,get_raw_table("tickets"))

#gives you everything, but you can easily index the list for what you want uwu
def filtered_date_games(date):
	filtered = filter(lambda a:a["date"]>=date,get_raw_table("games"))
	return sorted(filtered,key=lambda a:a["date"])

# Returns None if no game exists
# Returns game json object if game with id==game_id exists
def get_game(game_id):
	try:
		return filter(lambda a:a['id']==game_id,get_raw_table("games"))[0]
	except:
		return None

# Returns true if there is a ticket available to be bought for game with id == game_id or false if not
def is_ticket_available(game_id):
	today = datetime.datetime.now().strftime("%Y%m%d%H%M")
	game_time = filter(lambda a:a["id"]==game_id,get_raw_table("games"))[0]["date"]
	return len(filter(lambda a:a["game_id"]==game_id and a["for_lottery"]==0 and a["owner"]=="hokipoki" and game_time >= today ,get_raw_table("tickets"))) >0

# Returns true if the lottery is open for game with id == game_id or false if not
def is_lottery_available(game_id):
	return len(filter(lambda a:a["id"]==game_id and a["lottery_open"]==1,get_raw_table("games"))) > 0

# Returns true if user owns a ticket for game with id == game_id or false if not
def user_has_ticket(user,game_id):
    return len(filter(lambda a:a["game_id"] == game_id and a["owner"] == user,get_raw_table("tickets")))>0

# Returns true if user is in lottery for game with id == game_id or false if not
def user_in_lottery(user,game_id):
    return len(filter(lambda a:a["user"]==user and a["game_id"]==game_id,get_raw_table("lottoentries")))>0
