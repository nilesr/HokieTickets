#!python
from __future__ import print_function
import json
from libgoblin import *
import datetime

# try:
#     parsed = libgoblin.buy('ankita',3)
#     print(type(parsed))
#     print(json.dumps(parsed, indent=4, sort_keys=True))
# except Exception as e:
#     #print("TEST HAHAHAHAH GOTEEM")
#     print(e)


# try:
#     parsed = libgoblin.sell('ankita',3)
#     print(type(parsed))
#     print(json.dumps(parsed, indent=4, sort_keys=True))
# except Exception as e:
#     print(e)




# game_id = 1
# parsed = libgoblin.get_raw_table("tickets")
# filtered = filter(lambda a:a["game_id"]==game_id and a["for_lottery"]==0 and a["owner"]=="hokipoki",parsed)
# for item in filtered:
#     print(item)

# game_id = 3
# user = "bruh"

# a = libgoblin.buy(user,game_id)
# for item in a[0][1][0][3][0]:
#     print(item)

# table = libgoblin.get_raw_table("tickets")
# filtered = filter(lambda a:a["game_id"] == game_id and a["owner"] == user,table)
# ticket_id = filtered[0]["id"]

# a = libgoblin.sell(user,ticket_id)

# user='bruh'
# return filter(lambda a:a["owner"]==user,get_raw_table("tickets"))

# date = 20200305
# filtered = filter(lambda a:a["date"]>=date,get_raw_table("games"))
# b = sorted(filtered,key=lambda a:a["date"])
# for item in b:
#     print(item)

# game_id = 0
# filtered = filter(lambda a:a['id']==game_id,get_raw_table("games"))[0]
# print(filtered)

# game_id = 0
# today = datetime.datetime.now().strftime("%Y%m%d%H%M")
# game_time = filter(lambda a:a["id"]==game_id,get_raw_table("games"))[0]["date"]
# filtered = len(filter(lambda a:a["game_id"]==game_id and a["for_lottery"]==0 and a["owner"]=="hokipoki" and game_time >= today ,get_raw_table("tickets"))) >0
# print(filtered)

# def user_has_ticket(user,game_id):
#     return len(filter(lambda a:a["game_id"] == game_id and a["owner"] == user,get_raw_table("tickets")))>0
    
# print(user_has_ticket("bruh",0))
# buy("bruh",0)
# print(user_has_ticket("bruh",0))

# def user_in_lottery(user,game_id):
#     return len(filter(lambda a:a["user"]==user and a["game_id"]==game_id,get_raw_table("lottoentries")))>0
# print(user_in_lottery("bruh",0))
# print(user_in_lottery("bruh",1))

print(transfer("ankita", 999996219.32, "testing"))

#print(json.dumps(parsed,indent=4,sort_keys=True))

