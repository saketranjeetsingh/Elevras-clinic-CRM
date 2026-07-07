import json
import urllib.request
import urllib.error

base = 'http://127.0.0.1:8000'

data = 'username=delete.tester@example.com&password=Delete123!'.encode()
req = urllib.request.Request(base + '/auth/login', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
login = urllib.request.urlopen(req, timeout=5)
token = json.loads(login.read().decode())['access_token']
headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
patient = json.dumps({'name': 'Sprint3 Patient', 'phone': '9876543210', 'email': 'sprint3@example.com', 'age': 30, 'gender': 'Other', 'notes': '', 'last_treatment': ''}).encode()

req = urllib.request.Request(base + '/patients', data=patient, headers=headers, method='POST')
try:
    first = urllib.request.urlopen(req, timeout=5)
    print('first', first.status, first.read().decode())
except urllib.error.HTTPError as e:
    print('first_error', e.code, e.read().decode())

req = urllib.request.Request(base + '/patients', data=patient, headers=headers, method='POST')
try:
    urllib.request.urlopen(req, timeout=5)
except urllib.error.HTTPError as e:
    print('second', e.code, e.read().decode())
