#!/usr/bin/env python3

"""

This script will make a Jellyfin user account for each Plex user currently with access to your Plex Media Server (Sharing Users)
Each new user account will have the same Plex name as their Jellyfin username, and a blank password

"""

from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
import json
import random
import string
import time
import helpers.jellyfin as jf
import helpers.plex as px

plex = px.server

user_list = {}

def password(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def add_password(uid):
    p = password(length=10)
    payload = {
        "Id": uid,
        "CurrentPw": '',
        "NewPw": p,
        "ResetPassword": 'false'
     }
    r = jf.post('/Users/{}/Password'.format(str(uid)), None, payload=payload)
    if not str(r.status_code).startswith('2'):
        return False
    else:
        print(p)
        return p


def update_policy(uid):
    if not str(jf.post("Users/{}/Policy".format(str(uid)), None, payload=jf.user_policy).status_code).startswith('2'):
        return False
    else:
        return True

def make_jellyfin_user(username):
    try:
        p = None
        payload = {
            "Name": username
        }
        r = jf.post("Users/New", None, payload=payload)
        if not str(r.status_code).startswith('2'):
            return False, r.content.decode("utf-8"), p
        else:
            r = json.loads(r.text)
            uid = r['Id']
            #p = add_password(uid)
            if not p:
                p = None
            if update_policy(uid):
                return True, uid, p
            else:
                return False, uid, p
    except Exception as e:
        print(e)
        return False, None, None


def convert_plex_to_jellyfin(username):
    print("Adding " + username + " to Jellyfin...")
    succeeded, uid, pwd = make_jellyfin_user(username)
    if succeeded:
        user_list[username] = [uid, pwd]
        return True, None
    else:
        if uid:
            return False, uid
        else:
            return False, None

    return True, None


print("Beginning user migration...")
for user in plex.myPlexAccount().users():
    for s in user.servers:
        if s.name == PLEX_SERVER_NAME:
            success, failure_reason = convert_plex_to_jellyfin(user.username)
            if success:
                print(user.username + " added to Jellyfin.")
            else:
                print(user.username + " was not added to Jellyfin. Reason: " + str(failure_reason))
            #time.sleep(5)
            break
print("User migration complete.")
if user_list:
    print("\nUsername ---- Password")
    for k, v in user_list.items():
        print(str(k) + "  |  " + str(v[1]))