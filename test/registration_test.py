#!/usr/bin/env python3
"""
Tests for POST /users/post.php.
Run: python3 -m pytest registration_test.py
"""

import time
import unittest
from helpers import POST_URL, make_png, post, post_form


class RegistrationTest(unittest.TestCase):
    def test_register_with_name_email_and_password_returns_201(self):
        status, body = post({
            "name": "Jane Doe",
            "email": f"jane.doe.{int(time.time())}@example.com",
            "password": "hunter",
        })
        self.assertEqual(status, 201)

    def test_register_all_fields_returns_201(self):
        status, body = post({
            "name": "John Smith",
            "email": f"john.smith.{int(time.time())}@example.com",
            "password": "hunter",
            "graduation_year": 2010,
            "field_of_study": "Computer Science",
            "current_role": "Software Engineer",
            "company": "Acme Corp",
            "location": "New York, NY",
            "bio": "Alumni and proud member.",
        })
        self.assertEqual(status, 201)

    def test_register_all_fields_and_profile_picture_returns_201(self):
        status, body = post({
            "name": "Alice Brown",
            "email": f"alice.brown.{int(time.time())}@example.com",
            "password": "hunter",
            "graduation_year": 2015,
            "field_of_study": "Biology",
            "current_role": "Researcher",
            "company": "Lab Inc",
            "location": "Boston, MA",
            "bio": "Passionate about science.",
        }, {
            "profile_picture": ("avatar.png", bytes([
            0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a,0x00,0x00,0x00,0x0d,0x49,0x48,0x44,0x52,
            0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,
            0xde,0x00,0x00,0x00,0x0c,0x49,0x44,0x41,0x54,0x08,0xd7,0x63,0xf8,0xcf,0xc0,0x00,
            0x00,0x00,0x02,0x00,0x01,0xe2,0x21,0xbc,0x33,0x00,0x00,0x00,0x00,0x49,0x45,0x4e,
            0x44,0xae,0x42,0x60,0x82,
        ]), "image/png"),
        })
        self.assertEqual(status, 201)

    def test_register_with_max_size_profile_picture_returns_201(self):
        status, body = post_form(POST_URL, {
            "name": "Bob Max",
            "email": f"bob.max.{int(time.time())}@example.com",
            "password": "hunter",
        }, {
            "profile_picture": ("max.png", make_png(65536), "image/png"),
        })
        self.assertEqual(status, 201)

    def test_register_with_empty_name_fails(self):
        status, body = post({
            "name": "",
            "email": f"empty.name.{int(time.time())}@example.com",
            "password": "hunter",
        })
        self.assertEqual(status, 400, msg=body)
        self.assertEqual(body.get("error"), "missing_required_fields", msg=body)
        self.assertIn("name", body.get("fields", []), msg=body)


    # this test requires to be changed, as well as the code tested by it.
    def test_register_with_bigname_fails(self):
        status, body = post({
            "name": "A" * 128,
            "email": f"bigname.{int(time.time())}@example.com",
            "password": "hunter",
        })
        self.assertEqual(status, 500, msg=body)
        self.assertEqual(body.get("error"), "internal_error", msg=body)

    def test_register_with_empty_email_fails(self):
        status, body = post({
            "name": "Jane Doe",
            "email": "",
            "password": "hunter",
        })
        self.assertEqual(status, 400, msg=body)
        self.assertEqual(body.get("error"), "missing_required_fields", msg=body)
        self.assertIn("email", body.get("fields", []), msg=body)

    def test_register_with_invalid_email_fails(self):
        status, body = post({
            "name": "Jane Doe",
            "email": "not-an-email",
            "password": "hunter",
        })
        self.assertEqual(status, 400, msg=body)
        self.assertEqual(body.get("error"), "invalid_email", msg=body)

    # this test requires to be changed, as well as the code tested by it.
    def test_register_with_big_field_of_study_fails(self):
        status, body = post({
            "name": "Jane Doe",
            "email": f"big.fos.{int(time.time())}@example.com",
            "password": "hunter",
            "field_of_study": "A" * 128,
        })
        self.assertEqual(status, 500, msg=body)
        self.assertEqual(body.get("error"), "internal_error", msg=body)

    # this test requires to be changed, as well as the code tested by it.
    def test_register_with_big_current_role_fails(self):
        status, body = post({
            "name": "Jane Doe",
            "email": f"big.role.{int(time.time())}@example.com",
            "password": "hunter",
            "current_role": "A" * 128,
        })
        self.assertEqual(status, 500, msg=body)
        self.assertEqual(body.get("error"), "internal_error", msg=body)

    # this test requires to be changed, as well as the code tested by it.
    def test_register_with_big_company_fails(self):
        status, body = post({
            "name": "Jane Doe",
            "email": f"big.company.{int(time.time())}@example.com",
            "password": "hunter",
            "company": "A" * 128,
        })
        self.assertEqual(status, 500, msg=body)
        self.assertEqual(body.get("error"), "internal_error", msg=body)

    # this test requires to be changed, as well as the code tested by it.
    def test_register_with_big_location_fails(self):
        status, body = post({
            "name": "Jane Doe",
            "email": f"big.location.{int(time.time())}@example.com",
            "password": "hunter",
            "location": "A" * 128,
        })
        self.assertEqual(status, 500, msg=body)
        self.assertEqual(body.get("error"), "internal_error", msg=body)

    # this test requires to be changed, as well as the code tested by it.
    def test_register_with_big_bio_fails(self):
        status, body = post({
            "name": "Jane Doe",
            "email": f"big.bio.{int(time.time())}@example.com",
            "password": "hunter",
            "bio": "A" * 128,
        })
        self.assertEqual(status, 500, msg=body)
        self.assertEqual(body.get("error"), "internal_error", msg=body)


    def test_register_with_invalid_image_format_fails(self):
        status, body = post_form(POST_URL, {
            "name": "Jane Doe",
            "email": f"bad.img.{int(time.time())}@example.com",
            "password": "hunter",
        }, {
            "profile_picture": ("file.txt", b"not an image", "text/plain"),
        })
        self.assertEqual(status, 400, msg=body)
        self.assertEqual(body.get("error"), "invalid_file_type", msg=body)

    def test_register_with_too_large_image_fails(self):
        status, body = post_form(POST_URL, {
            "name": "Jane Doe",
            "email": f"big.img.{int(time.time())}@example.com",
            "password": "hunter",
        }, {
            "profile_picture": ("big.png", make_png(65537), "image/png"),
        })
        self.assertEqual(status, 400, msg=body)
        self.assertEqual(body.get("error"), "file_too_large", msg=body)


if __name__ == "__main__":
    unittest.main()
