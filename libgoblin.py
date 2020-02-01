#!/usr/bin/env python2
import json, subprocess, collections
cleos = ["cleos", "--no-auto-keosd", "-u", "http://127.0.0.1:8888", "--wallet-url", "unix:///home/ubuntu/eosio-wallet/keosd.sock"]


#########################################################
## Restart mako-server every time you change this file ##
#########################################################


def _try_symbolize_names(l):
	if not isinstance(l, dict): return l
	l = {k: _try_symbolize_names(v) for k, v in l.items()} # recurse
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
