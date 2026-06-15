import http.cookiejar
import json
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib


BASE_URL = "http://35.208.59.90"
POST_URL  = f"{BASE_URL}/users/post.php"
LOGIN_URL = f"{BASE_URL}/users/login.php"


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
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def post(data, files=None):
    return post_form(POST_URL, data, files)


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