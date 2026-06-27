#!/usr/bin/env python3
"""
Tests for POST /users/login.php.
Run: python3 -m pytest login_test.py
"""

import time
import unittest
from helpers import post, login, logout, delete


class LoginTest(unittest.TestCase):
    def test_register_login_delete(self):
        email = f"login.smoke.{int(time.time())}@example.com"
        password = "hunter"

        status, body = post({"name": "Test User", "email": email, "password": password})
        self.assertEqual(status, 201)
        user_id = body["id"]

        status, body = login(email, password)
        self.assertEqual(status, 200)

        status, body = logout()
        self.assertEqual(status, 200)

        status, body = login(email, password)
        self.assertEqual(status, 200)

        status, body = delete(user_id)
        self.assertEqual(status, 200)
        self.assertEqual(body.get("deleted"), user_id)


if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()
