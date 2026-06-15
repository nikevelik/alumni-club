import http.cookiejar
import json
import time
import urllib.error
import urllib.parse
import urllib.request


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