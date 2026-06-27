#!/usr/bin/env python3
"""
Tests for POST /users/login.php.
Run: python3 -m pytest unit/loginTest.py
"""

import time
import unittest
from helpers import post, post_form, login, delete, LOGIN_URL


def register(email, password="hunter"):
    return post({"name": "Test User", "email": email, "password": password})


class LoginTest(unittest.TestCase):
    def test_login_with_email_and_password_returns_200(self):
        email = f"login.{int(time.time())}@example.com"
        password = "hunter"

        _, body = register(email, password)
        user_id = body["id"]

        status, body = login(email, password)
        self.assertEqual(status, 200)
        self.assertEqual(body.get("id"), user_id)
        self.assertTrue(body.get("logged_in"))

        delete(user_id)

    def test_login_when_logged_returns_200(self):
        email = f"login.already.{int(time.time())}@example.com"
        password = "hunter"

        _, body = register(email, password)
        user_id = body["id"]

        login(email, password)
        status, body = login(email, password)
        self.assertEqual(status, 200)
        self.assertTrue(body.get("logged_in"))

        delete(user_id)

    def test_login_with_invalid_credentials_returns_401(self):
        status, body = login(f"nonexistent.{int(time.time())}@example.com", "hunter")
        self.assertEqual(status, 401)
        self.assertEqual(body.get("error"), "invalid_credentials")

    def test_login_with_empty_email_fails(self):
        status, body = login("", "hunter")
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "missing_required_fields")
        self.assertIn("email", body.get("fields", []))

    def test_login_with_empty_password_fails(self):
        status, body = login(f"empty.pw.{int(time.time())}@example.com", "")
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "missing_required_fields")
        self.assertIn("password", body.get("fields", []))

    def test_login_with_missing_email_fails(self):
        status, body = post_form(LOGIN_URL, {"password": "hunter"})
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "missing_required_fields")
        self.assertIn("email", body.get("fields", []))

    def test_login_with_missing_password_fails(self):
        status, body = post_form(LOGIN_URL, {"email": f"missing.pw.{int(time.time())}@example.com"})
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "missing_required_fields")
        self.assertIn("password", body.get("fields", []))


if __name__ == "__main__":
    unittest.main()
