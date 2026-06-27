#!/usr/bin/env python3
"""
Tests for POST /users/logout.php.
Run: python3 -m pytest integration/logoutIT.py
"""

import time
import unittest
from helpers import post, login, logout, delete


def register(email, password="hunter"):
    return post({"name": "Test User", "email": email, "password": password})


class LogoutTest(unittest.TestCase):
    def test_logout_without_session_returns_401(self):
        status, body = logout()
        self.assertEqual(status, 401)
        self.assertEqual(body.get("error"), "not_logged_in")

    def test_logout_after_login_returns_200(self):
        email = f"logout.{int(time.time())}@example.com"
        password = "hunter"

        _, body = register(email, password)
        user_id = body["id"]

        login(email, password)
        status, body = logout()
        self.assertEqual(status, 200)
        self.assertEqual(body.get("logged_out"), user_id)

        delete(user_id)

    def test_logout_twice_returns_401_on_second_call(self):
        email = f"logout.twice.{int(time.time())}@example.com"
        password = "hunter"

        _, body = register(email, password)
        user_id = body["id"]

        login(email, password)
        logout()
        status, body = logout()
        self.assertEqual(status, 401)
        self.assertEqual(body.get("error"), "not_logged_in")

        delete(user_id)


if __name__ == "__main__":
    unittest.main()
