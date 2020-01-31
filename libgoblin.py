#!/usr/bin/env python2
import json, subprocess, collections
cleos = ["cleos", "--no-auto-keosd", "-u", "http://127.0.0.1:8888", "--wallet-url", "unix:///home/ubuntu/eosio-wallet/keosd.sock"]


#########################################################
## Restart mako-server every time you change this file ##
#########################################################


def _try_symbolize_names(l):
	if not isinstance(l, dict): return l
	cls = collections.namedtuple("t", l.keys())
	cls.__getitem__ = lambda self, k: l[k]
	return cls(**l)

def _exec(l):
	if not isinstance(l, list): raise TypeError("Invalid object passed to libgoblin._exec(): {}".format(str))
	result = json.loads(subprocess.check_output(cleos + l).decode("utf-8"))
	return _try_symbolize_names(result)

def get_info():
	return _exec(["get", "info"])
