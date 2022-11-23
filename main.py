#!/usr/bin/env python2.7
# encoding: utf-8

import sys
import time
import threading

import click
import yaml

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
        for key, value in query.iteritems():
            # Попытка просто обратиться к query приводит к падению с KeyError
            if key == "oauth_token":
                OAUTH_TOKEN = value
            if key == "oauth_verifier":
                OAUTH_VERIFIER = value

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head></head><body><p>Success</p></body></html>")


def http_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, OauthRequestHandler)
    httpd.serve_forever()


def get_access_token():
    global OAUTH_TOKEN
    global OAUTH_VERIFIER

    hs = threading.Thread(
        target=http_server
    )
    hs.daemon = True
    hs.start()

    client = EvernoteClient(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        sandbox=True  # Default: True
    )
    request_token = client.get_request_token(CALLBACK_URL)
    print request_token

    print client.get_authorize_url(request_token)

    while not OAUTH_TOKEN:
        # print "Waiting for oauth_token"
        time.sleep(1)

    access_token = client.get_access_token(
        request_token['oauth_token'],
        request_token['oauth_token_secret'],
        OAUTH_VERIFIER,
    )
    print access_token


def main():
    try:
        with open('secrets.yaml', 'r') as f_secrets:
            secrets = yaml.safe_load(f_secrets)
    except IOError:
        click.echo(
            click.style("Can't load secrets from secrets.yaml file", fg="red")
        )
        return
    except yaml.YAMLError:
        click.echo(
            click.style("secrets.yaml file corrupted", fg="red")
        )
        return

    access_token = secrets.get("access_token")
    if not access_token:
        click.echo(
            click.style("access_token in empty or not exists", fg="red")
        )

    client = EvernoteClient(token=access_token)
    note_store = client.get_note_store()
    notebooks = note_store.listNotebooks()

    # Обкачивать аккаунт надо через SyncChunk



if __name__ == '__main__':
    sys.exit(main())
