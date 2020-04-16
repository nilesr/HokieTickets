#!/usr/bin/env python2
import json, subprocess, collections, random, re, datetime, time, struct, qrcode, io, base64
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
    def __str__(self):
	return "EosioError(output={})".format(self.output)

def _try_symbolize_names(l):
	if isinstance(l, list): return [_try_symbolize_names(i) for i in l]
	if not isinstance(l, dict): return l
	l = {k if k not in KEYWORDS else k + "_": _try_symbolize_names(v) for k, v in l.items()} # recurse
	cls = collections.namedtuple("t", l.keys())
	old_getitem = cls.__getitem__
	cls.__getitem__ = lambda self, k: l[k] if isinstance(k, str) else old_getitem(self, k)
	return cls(**l)

def _try_desymbolize_names(l):
	if isinstance(l, list): return [_try_desymbolize_names(i) for i in l]
	if isinstance(l, dict): return {k: _try_desymbolize_names(v) for k, v in l.items()}
	if not (isinstance(l, tuple) and not type(l) == tuple): return l
	return l.__dict__


def _exec(l, json_decode = True):
	if not isinstance(l, list): raise TypeError("Invalid object passed to libgoblin._exec(): {}".format(str))
	proc = subprocess.Popen(cleos + l, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()
	stdout = stdout.decode("utf-8")
	stderr = stderr.decode("utf-8")
	if proc.returncode != 0:
		raise EosioError(stderr)
	if json_decode:
		try:
			return _try_symbolize_names(json.loads(stdout))
		except Exception as e:
			print(stdout)
			raise e
	return stdout

def wrap_exec(with_result, *args, **kwargs):
    try:
	if with_result:
	    return with_result(_exec(*args, **kwargs))
	else:
	    return _exec(*args, **kwargs)
    except EosioError as e:
	try:
	    return json.dumps({"error": re.sub(u'\u001b\[.*?[@-~]', '', e.output.split("message: ")[1].replace("pending console output:", "").replace("\n",""))})
	except:
	    return json.dumps({"error": e.output})

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

def repeat_exec(*args, **kwargs):
    rows = []
    r = _exec(*args, **kwargs)
    rows += r.rows
    while r.more:
	r = _exec(*args, **kwargs)
	rows += r.rows
    return rows

def get_raw_table(table):
	return repeat_exec(["get", "table", "-l", "-1", "hokipoki", "hokipoki", table])

def get_declared_tables():
	return [t.name for t in _exec(["get", "abi", "hokipoki"]).tables]

def create_account(user):
	keymat = list(map(lambda x: x.split(),_exec(["create", "key", "--to-console"], False).split("\n")))
	priv = keymat[0][2]
	pub = keymat[1][2]
	import_key(priv)
	_exec(["create", "account", "eosio", user, KEY], False)
	_exec(["set", "account", "permission", user, "active",
		'{"threshold":1, "keys":[{"key":"'+pub+'", "weight":1}], "accounts": [{"permission":{"actor":"hokipoki","permission":"eosio.code"},"weight":1}]}',
		"owner", "-p", user + "@owner"], False)
	_exec(["push", "action", "hokipoki", "adduser", json.dumps([user]), "-p", "hokipoki@active"], False)
	return pub, priv

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
    ticket_id = -1
    filtered = filter(lambda a:a["for_lottery"]==0 and a["owner"]=="hokipoki",get_tickets_for_game(game_id))
    if len(filtered) > 0:
	ticket_id= filtered[0]["id"]
    #TODO: Error if ticket is not available
    def with_result(r):
	return json.dumps({"balance":get_balance(user)})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "buy", json.dumps([user, ticket_id]), "-p", user + "@active", "-j"])

def sell(user, ticket_id):
    def with_result(r):
	return json.dumps({"balance":get_balance(user)})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "sell", json.dumps([user, ticket_id]), "-p", user + "@active", "-j"])

def enter_lottery(user, game_id):
    r1 = random.randint(0, 2 ** 64 - 1)
    r2 = random.randint(0, 2 ** 64 - 1)
    r3 = random.randint(0, 2 ** 64 - 1)
    r4 = random.randint(0, 2 ** 64 - 1)
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "enterlottery", json.dumps([user, game_id, r1, r2, r3, r4]), "-p", user + "@active", "-j"])

def leave_lottery(user, game_id):
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "leavelottery", json.dumps([user, game_id]), "-p", user + "@active", "-j"])

def create_auction(user, ticket_id, initial_bid, end_date):
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "creatauction", json.dumps([ticket_id, initial_bid, end_date]), "-p", user + "@active", "-j"])

def bid(ticket_id, user, bid):
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "bid", json.dumps([ticket_id, user, bid]), "-p", user + "@active", "-j"])

def execute_auction_winner(ticket_id, user):
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "execauction1", json.dumps([ticket_id]), "-p", user + "@active", "-j"])

def execute_auction_owner(ticket_id, user):
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "execauction2", json.dumps([ticket_id]), "-p", user + "@active", "-j"])

def cancel_auction(ticket_id, user):
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "cancelauctn", json.dumps([ticket_id]), "-p", user + "@active", "-j"])


# ADMIN ACTIONS
def execute_lottery(game_id):
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "executelotto", json.dumps([game_id]), "-p", "hokipoki@active", "-j"])

def open_lottery(game_id):
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "openlottery", json.dumps([game_id]), "-p", "hokipoki@active", "-j"])

def create_game(day, num_tickets, tickets_for_lotto, price, name, location, lottery_opens, lottery_closes, reward, game_type):
	return wrap_exec(False, ["push", "action", "hokipoki", "creategame", json.dumps([day, num_tickets, tickets_for_lotto, price, name, location, lottery_opens, lottery_closes, reward, game_type]), "-p", "hokipoki@active", "-j"])

def execute_all_auctions(game_id):
    def with_result(r):
	return json.dumps({"success":"Success!"})
    return wrap_exec(with_result, ["push", "action", "hokipoki", "aucexecall", json.dumps([game_id]), "-p", "hokipoki@active", "-j"])

def reset():
	return wrap_exec(False, ["push", "action", "hokipoki", "reset", json.dumps([]), "-p", "hokipoki@active", "-j"])

def transfer(user, amount, message):
    amount_str = str(amount)
    if "." not in amount_str:
	amount_str = amount_str + ".00 HTK"
    elif len(amount_str.split(".")[1]) != 2:
	amount_str = amount_str + "0 HTK"
    else:
	amount_str = amount_str + " HTK"
    def with_result(r):
	return json.dumps({"balance":get_balance(user)})
    return wrap_exec(with_result, ["push", "action", "eosio.token", "transfer", json.dumps(["hokipoki", user, amount_str, message]), "-p", "hokipoki@active", "-j"])

#REQUESTS RECIEVED FROM RACHEL

#returns all tickets that a user owns
def user_tickets(user):
	return filter(lambda a:a["owner"]==user,get_raw_table("tickets"))

#gives you everything, but you can easily index the list for what you want
def filtered_date_games(date):
	filtered = filter(lambda a:a["date"]>=date,get_raw_table("games"))
	return sorted(filtered,key=lambda a:a["date"])

# Returns None if no game exists
# Returns game json object if game with id==game_id exists
def get_game(game_id):
	try:
		return repeat_exec(["get", "table", "hokipoki", "hokipoki", "games", "-l", "-1", "-L", str(game_id), "-U", str(game_id)])[0]
	except:
		return None

def get_ticket(ticket_id):
	try:
		return repeat_exec(["get", "table", "hokipoki", "hokipoki", "tickets", "-l", "-1", "-L", str(ticket_id), "-U", str(ticket_id)])[0]
	except:
		return None

def get_auction(ticket_id):
	try:
		return repeat_exec(["get", "table", "hokipoki", "hokipoki", "auctions", "-l", "-1", "-L", str(ticket_id), "-U", str(ticket_id)])[0]
	except:
		return None

def get_tickets_for_game(game_id):
	try:
		return repeat_exec(["get", "table", "hokipoki", "hokipoki", "tickets", "--index", "2", "--key-type", "i64", "-l", "-1", "-L", str(game_id), "-U", str(game_id)])
	except:
		return None

# Returns true if there is a ticket available to be bought for game with id == game_id or false if not
def is_ticket_available(game_id):
	today = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
	game_time = get_game(game_id).date
	return len(filter(lambda a:a["for_lottery"]==0 and a["owner"]=="hokipoki" and game_time >= today ,get_tickets_for_game(game_id))) >0

# Returns true if the lottery is open for game with id == game_id or false if not
def is_lottery_available(game_id):
    return get_game(game_id).lottery_open == 1

# Returns true if user owns a ticket for game with id == game_id or false if not
def user_has_ticket(user,game_id):
    stuff = filter(lambda a:a["owner"] == user,get_tickets_for_game(game_id))
    return stuff[0] if len(stuff) > 0 else False

def get_lottery_entries_by_user(user):
    return repeat_exec(["get", "table", "hokipoki", "hokipoki", "lottoentries", "--index", "2", "--key-type", "i64", "-l", "-1", "-L", user, "-U", user])
def get_lottery_entries_by_game(game_id):
    return repeat_exec(["get", "table", "hokipoki", "hokipoki", "lottoentries", "--index", "3", "--key-type", "i64", "-l", "-1", "-L", str(game_id), "-U", str(game_id)])

# Returns true if user is in lottery for game with id == game_id or false if not
def user_in_lottery(user,game_id):
    return len(filter(lambda a:a["game_id"]==game_id,get_lottery_entries_by_user(user)))>0


def get_history(user):
    results = _exec(["get", "actions", user, "-j", "-1", "-100000000000"]).actions
    l = []
    last = None
    lastact = None
    for r in results:
	if r.action_trace.trx_id == last:
	    if r.action_trace.receipt.act_digest == lastact:
		continue
	    l[-1].append(r)
	else:
	    l.append([r])
	    last = r.action_trace.trx_id
	lastact = r.action_trace.receipt.act_digest
    return l

# Returns the number of tickets reserved for the lottery
def get_num_of_lottery(game_id):
    	return len(filter(lambda a:a["for_lottery"],get_tickets_for_game(game_id)))

#Returns a list of users in the lottery for the given game_id
def lottery_entries_by_game(game_id):
    return [b.user for b in get_lottery_entries_by_game(game_id)]
    
#Returns the past tickets from a given user
def get_past_tickets(user):
	today = datetime.datetime.now().strftime("%Y%m%d%H%M")
	games = get_raw_table("games")
	dates = {game.id: game.date for game in games}
	return filter(lambda a:a.owner == user and (today > dates.get(a.game_id, today) or a.attended == True), get_raw_table("tickets")) # TODO put a "by owner" index on the tickets table, so we don't have to do a full table scan here



def transfer_from(from_user, to_user, amount, message):
    amount_str = str(amount)
    if "." not in amount_str:
	amount_str = amount_str + ".00 HTK"
    elif len(amount_str.split(".")[1]) != 2:
	amount_str = amount_str + "0 HTK"
    else:
	amount_str = amount_str + " HTK"
    def with_result(r):
	return json.dumps({"balance": get_balance(to_user)})
    return wrap_exec(with_result, ["push", "action", "eosio.token", "transfer", json.dumps([from_user,to_user, amount_str, message]), "-p", from_user+"@active", "-j"])


# Penalizes users for not attending games
def penalize_users(game_id):
    penalty_amount = "5"
    tickets = filter(lambda a:a["game_id"] == game_id,get_raw_table("tickets"))
    r = []
    for ticket in tickets:
        if not ticket["attended"] and not ticket["owner"]=="hokipoki":
            user = ticket["owner"]
            user_balance = get_balance(user)
            if (user_balance - float(penalty_amount)) < 0:
                penalty_amount = str(user_balance)
            transfer_from(user,"hokipoki",penalty_amount,"Penalty for not attending game")
            r.append(user)
    return r

def reward_user(ticket_id):
    def with_result(r):
	return {"success": "Success!"}
    owner = get_ticket(ticket_id).owner
    return wrap_exec(with_result, ["push", "action", "hokipoki", "rewarduser", json.dumps([ticket_id]), "-p", "hokipoki@active", "-p", owner + "@active", "-j"])

def active_tickets(user):
	r = []
	now = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
	return filter(lambda a: a["owner"] == user and not a.attended and int(get_game(a.game_id).date) >= now, get_raw_table("tickets"))

def get_game_type(game_id):
	games = {
		0: "Football",
		1: "Men's Basketball",
		2: "Women's Basketball",
		3: "Men's Soccer",
		4: "Women's Soccer", 
		5: "Baseball",
		6: "Cross Country",
		7: "Men's Golf",
		8: "Women's Golf",
		9: "Lacrosse",
		10: "Softball",
		11: "Swim and Dive",
		12: "Men's Tennis",
		13: "Women's Tennis",
		14: "Track and Field",
		15: "Volleyball",
		16: "Wrestling"
	} 
	return games.get(game_id, "Invalid Game ID")


def format_date(date):
    d = str(date)[:8]
    return time.strftime("%A, %B %-d, %Y", time.strptime(d, "%Y%m%d"))

def format_datetime(dt):
    d = str(dt)
    return time.strftime("%-l:%M %P on %A, %B %-d, %Y", time.strptime(d, "%Y%m%d%H%M%S"))


# AUCTION HELPERS

def auction_for_ticket_id(ticket_id):
	return get_auction(ticket_id) != None

def get_ticket_by_id(ticket_id):
	return get_ticket(ticket_id)

def get_auction_by_ticket_id(ticket_id):
	auction = get_auction(ticket_id)
	if not auction:
		return( json.dumps({"error": "No auction exists"}) )
	dt_string = datetime.datetime.now().strftime("%Y%m%d%H%M")
	if int(auction[0]) < int(dt_string):
		return( json.dumps({"error": "Auction ended"}) )
	else:
		return( auction )

def auction_ended(ticket_id):
	auction = get_auction(ticket_id)
	dt_string = datetime.datetime.now().strftime("%Y%m%d%H%M")
	return int(auction[0]) < int(dt_string)

def get_auctions_by_name(user):
	auctions = filter(lambda a:a["auction_owner"] == user, get_raw_table("auctions"))
	return auctions

def get_auctions_by_game(game_id):
	auctions = filter(lambda a:a["game_id"] == game_id, get_raw_table("auctions"))
	return to_json({"Success": list(auctions)})

def get_auctions_user_bid(user):
	auctions = filter(lambda a:a["top_bidder"] == user, get_raw_table("auctions"))
	return auctions
	# return json.dumps({"Success": auctions})

def get_auction_groups():
    now = int(time.strftime("%Y%m%d%H%M", time.localtime()))
    games = get_raw_table("games")
    games = list(filter(lambda g: int(g.date) > now, games))
    games.sort(key=lambda g: g.date)
    auctions = get_raw_table("auctions")
    return [[g, list(filter(lambda a: a.game_id == g.id and a.end_date > now, auctions))] for g in games]

def get_qr_code_key_byte(s, i):
    secret = [
	0x6b, 0x34, 0x4c, 0xbf, 0xa8, 0x4c, 0x52, 0x42, 0x6b, 0x0b, 0xbf, 0x44,
	0xf7, 0x14, 0xb7, 0x96, 0xaa, 0xef, 0x3d, 0x44, 0x81, 0x2a, 0x01, 0xea,
	0x7c, 0xa9, 0x6c, 0x0c, 0xa3, 0x67, 0x92, 0x0b, 0x83, 0x4f, 0x87, 0xa7,
	0xd5, 0xa5, 0xdf, 0x41, 0xb5, 0x2f, 0xdf, 0xe4, 0x84, 0xb3, 0x88, 0x5e,
	0xbf, 0x0e, 0xac, 0x10, 0x26, 0xa4, 0x81, 0x8b, 0x63, 0x05, 0xc3, 0xe2,
	0x63, 0xd9, 0xce, 0xe8
    ]
    return secret[i % len(secret)] ^ s

def get_qr_code_data(ticket_id):
    data = b"HOKIPOKI" + struct.pack(">Q", ticket_id) + get_ticket(ticket_id).owner.encode()
    s = random.randint(0, 255)
    data = b"".join([chr(s)] + [chr(ord(c) ^ get_qr_code_key_byte(s, i)) for i, c in enumerate(data)])
    return base64.b64encode(data)

def get_qr_code(ticket_id):
    data = get_qr_code_data(ticket_id)
    i = io.BytesIO();
    #qrcode.make(data).get_image().save(i, format="PNG")
    qr = qrcode.QRCode(error_correction=random.choice([qrcode.constants.ERROR_CORRECT_H, qrcode.constants.ERROR_CORRECT_M, qrcode.constants.ERROR_CORRECT_L]))
    qr.add_data(data)
    qr.make()
    qr.make_image().save(i, format="PNG")
    i.seek(0)
    return i.read()

def get_qr_code_data_uri(ticket_id):
    return "data:image/png;base64," + base64.b64encode(get_qr_code(ticket_id))

def scan_qr_code(data):
    data = base64.b64decode(data)
    data = b"".join([chr(ord(c) ^ get_qr_code_key_byte(ord(data[0]), i)) for i, c in enumerate(data[1:])])
    if data[:len("HOKIPOKI")].decode() != "HOKIPOKI":
	return {"error": "The magic number is invalid"}
    ticket_id = struct.unpack(">Q", data[len("HOKIPOKI"):len("HOKIPOKI")+8])[0]
    owner = data[len("HOKIPOKI")+8:]
    t = get_ticket(ticket_id)
    if not t:
	return {"error": "That ticket does not exist"}
    if t.owner != owner:
	return {"error": "That ticket no longer belongs to the user who generated the QR code"}
    if t.attended == 1:
	return {"success": "That ticket has already been scanned!"}
    return reward_user(ticket_id)

def to_json(data):
    return json.dumps(_try_desymbolize_names(data))

def s(thing):
    return "" if len(thing) == 1 else "s"

def get_active_public_keys(user):
	ui = get_user_info(user)
	ps = [x for x in ui.permissions if x.perm_name == "active"]
	if len(ps) != 1: return False
	return [o.key for o in ps[0].required_auth.keys]

def import_key(priv):
    proc = subprocess.Popen(cleos + ["wallet", "import"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate(input=priv.encode())
    if proc.returncode != 0:
	raise EosioError(out.decode() + "\n" + err.decode())
