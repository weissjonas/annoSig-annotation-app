from kivy.network.urlrequest import UrlRequest
import urllib
import json
import sys

#API_URL = "https://95.217.13.152:8000"
# API_URL = "https://127.0.0.1:8000"

API_TOKEN = "0e2d70b1f642f85550adb7ff20656462"
'''
URL
https://95.217.13.152:8000/upload
HEADER
{'User-Agent': 'python-requests/2.22.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive', 'Authorization': '0e2d70b1f642f85550adb7ff20656462', 'Content-Length': '18', 'Content-Type': 'application/json'}
BODY
b'{"I": "break you"}'
'''

def my_error(request,error):
    print(request)
    print(error)
    

if __name__ == '__main__':
    var = '"bar", "baz"]}{"foo": ["bar", "baz"]}{"foo" ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo" ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo" ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo" ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo" ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo" ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo" ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": {"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}{"foo": ["bar", "baz"]}'

    print(UrlRequest('https://95.217.13.152:8000/upload', 
                 req_body=var,
                 req_headers={"Authorization": "0e2d70b1f642f85550adb7ff20656462"},
                 #ca_file="ssl/ca.pem",
                 verify=False
                 ).wait())
    print(sys.getsizeof(var))