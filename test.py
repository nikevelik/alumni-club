#!/usr/bin/env python3
"""
Tests for POST /users/post.php.
Run: python3 test.py
"""

import http.cookiejar
import json
import sys
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


def post_form(url, data):
    """POST form-encoded data; return (status, body_dict)."""
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=encoded, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def post(data):
    return post_form(POST_URL, data)


def assert_eq(label, actual, expected):
    ok = actual == expected
    mark = "OK " if ok else "FAIL"
    print(f"  [{mark}] {label}: got {actual!r}")
    if not ok:
        print(f"        expected {expected!r}")
    return ok


def printbody(body):
    if 1: 
        print()
        print()
        print()
        print(body)
        print()
        print()
        print()


def test_register_with_name_email_and_password_returns_201():
    print("=== TestRegisterWithNameEmailAndPasswordReturns201 ===")
    unique_email = f"jane.doe.{int(time.time())}@example.com"
    status, body = post({
        "name": "Jane Doe",
        "email": unique_email,
        "password": 'a' * 180,
    })
    printbody(body)
    return [
        assert_eq("status", status, 201),
    ]


def main():
    results = []

    results.extend(test_register_with_name_email_and_password_returns_201())

    print()
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"{passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
