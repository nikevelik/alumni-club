import http.cookiejar
import json
import os
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib

from dotenv import dotenv_values


_ENV = dotenv_values(os.path.join(os.path.dirname(__file__), "..", ".env"))

BASE_URL   = _ENV.get("BASE_URL")
POST_URL   = f"{BASE_URL}/users/post.php"
LOGIN_URL  = f"{BASE_URL}/users/login.php"
LOGOUT_URL = f"{BASE_URL}/users/logout.php"
DELETE_URL = f"{BASE_URL}/users/delete.php"

EVENT_GET_URL     = f"{BASE_URL}/events/get.php"
EVENT_GET_ALL_URL = f"{BASE_URL}/events/get_all.php"
EVENT_POST_URL    = f"{BASE_URL}/events/post.php"
EVENT_DELETE_URL  = f"{BASE_URL}/events/delete.php"


COOKIE_JAR = http.cookiejar.CookieJar()
urllib.request.install_opener(
    urllib.request.build_opener(urllib.request.HTTPCookieProcessor(COOKIE_JAR))
)


def post_form(url, fields, files=None):
    if not files:
        encoded = urllib.parse.urlencode(fields).encode("utf-8")
        req = urllib.request.Request(url, data=encoded, method="POST")
    else:
        boundary = "----FormBoundary" + str(int(time.time()))
        body = b""
        for name, value in fields.items():
            body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
        for name, (filename, content, mime) in files.items():
            body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"\r\nContent-Type: {mime}\r\n\r\n".encode()
            body += content + b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req) as resp:
            status, body = resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        status, body = e.code, json.loads(e.read())
    # DEBUG: print every response so failing tests show the full body
    # (including the 'debug' field added by Controller::respond on 500s).
    print(f"[{status}] POST {url} -> {json.dumps(body)[:500]}", flush=True)
    return status, body


def post(data, files=None):
    return post_form(POST_URL, data, files)


def login(email, password):
    return post_form(LOGIN_URL, {"email": email, "password": password})


def logout():
    return post_form(LOGOUT_URL, {})


def delete(user_id):
    return post_form(DELETE_URL, {"id": user_id})


def get_json(url, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            status, body = resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        status, body = e.code, json.loads(e.read())
    print(f"[{status}] GET {url} -> {json.dumps(body)[:500]}", flush=True)
    return status, body


def event_get(event_id):
    return get_json(EVENT_GET_URL, {"id": event_id})


def event_get_raw(params):
    # Lets a test send malformed/missing params (no urlencode coercion).
    return get_json(EVENT_GET_URL, params) if params else get_json(EVENT_GET_URL)


def event_get_all(query=None):
    return get_json(EVENT_GET_ALL_URL, {"query": query} if query is not None else None)


def event_create(fields):
    return post_form(EVENT_POST_URL, fields)


def event_delete(event_id):
    return post_form(EVENT_DELETE_URL, {"id": event_id})


def event_delete_raw(fields):
    return post_form(EVENT_DELETE_URL, fields)


def make_png(target_size):
    def chunk(name, data):
        c = name + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(b'\x00\xff\x00\x00'))
    iend = chunk(b'IEND', b'')
    base = sig + ihdr + idat + iend
    pad_len = target_size - len(base) - 12
    text = chunk(b'tEXt', b'Comment\x00' + b'A' * (pad_len - 8))
    return sig + ihdr + idat + text + iend