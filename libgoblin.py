#!/usr/bin/env python2
import json, subprocess, collections
cleos = ["cleos", "--no-auto-keosd", "-u", "http://127.0.0.1:8888", "--wallet-url", "unix:///home/ubuntu/eosio-wallet/keosd.sock"]
KEY = "EOS7J1tYpCHkCCvi5DwYXkJMRKRzK9XAUVvMC7PnrcucNXS6ZuMC1"
KEYWORDS = {"from", "except", "if", "else", "elif", "return"}


#########################################################
## Restart mako-server every time you change this file ##
#########################################################


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
	result = subprocess.check_output(cleos + l).decode("utf-8")
	if json_decode:
		return _try_symbolize_names(json.loads(result))
	return result

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

def buy(user, ticket_id):
	return _exec(["push", "action", "hokipoki", "buy", json.dumps([user, ticket_id]), "-p", user + "@active", "-j"])
def sell(user, ticket_id):
	return _exec(["push", "action", "hokipoki", "sell", json.dumps([user, ticket_id]), "-p", user + "@active", "-j"])

