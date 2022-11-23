#!/usr/bin/env python2.7

import sys
import time
import threading

from urlparse import parse_qs, urlparse
from evernote.api.client import EvernoteClient

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler


CONSUMER_KEY = ""
CONSUMER_SECRET = ""
CALLBACK_URL = "http://127.0.0.1:8080"

OAUTH_TOKEN = ""
OAUTH_VERIFIER = ""


class OauthRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global OAUTH_TOKEN
        global OAUTH_VERIFIER

        query = parse_qs(urlparse(self.path).query)
        for key in query.keys():
            print query[key]
            if key == "oauth_token":
                print "oauth_token found"
            print query["oauth_token"]

        OAUTH_TOKEN = query["oauth_token"][0]
        OAUTH_VERIFIER = query["oauth_verifier"][0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head></head><body><p>Success</p></body></html>")


def http_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, OauthRequestHandler)
    httpd.serve_forever()


def main():
    global OAUTH_TOKEN
    global OAUTH_VERIFIER

    hs = threading.Thread(
        target=http_server
    )
    hs.daemon = True
    hs.start()
    #
    # client = EvernoteClient(
    #     consumer_key=CONSUMER_KEY,
    #     consumer_secret=CONSUMER_SECRET,
    #     sandbox=True  # Default: True
    # )
    # request_token = client.get_request_token(CALLBACK_URL)
    # print request_token
    #
    # print client.get_authorize_url(request_token)

    while not OAUTH_TOKEN:
        # print "Waiting for oauth_token"
        time.sleep(1)

    # access_token = client.get_access_token(
    #     request_token['oauth_token'],
    #     request_token['oauth_token_secret'],
    #     OAUTH_VERIFIER,
    # )
    # print access_token


if __name__ == '__main__':
    sys.exit(main())
