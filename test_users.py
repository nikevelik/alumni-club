#!/usr/bin/env python3
"""
End-to-end tests for the /users/ endpoints.
Run: python3 test_users.py

Auth model: every endpoint except POST /users/post.php (registration) and
POST /users/login.php is gated behind a session cookie. Tests register a
throwaway account, log in, and run all gated assertions through that
authenticated session. The cookie is held in a CookieJar bound to the global
opener so urlopen() carries it on every request automatically.
"""

import http.cookiejar
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


BASE_URL = "http://35.208.59.90"
GET_URL      = f"{BASE_URL}/users/get.php"
GET_ALL_URL  = f"{BASE_URL}/users/get_all.php"
POST_URL     = f"{BASE_URL}/users/post.php"
DELETE_URL   = f"{BASE_URL}/users/delete.php"
PATCH_URL    = f"{BASE_URL}/users/patch.php"
LOGIN_URL    = f"{BASE_URL}/users/login.php"
LOGOUT_URL   = f"{BASE_URL}/users/logout.php"


# Single CookieJar shared across all requests. Re-installing on the global
# opener is what makes urllib.request.urlopen() send the PHPSESSID cookie back
# automatically once login.php sets it.
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


def post_multipart(url, fields, files):
    """POST multipart/form-data; return (status, body_dict).

    fields: dict of str -> str
    files:  dict of field_name -> (filename, content_bytes, content_type)
    """
    boundary = f"----pytest{uuid.uuid4().hex}"
    body = bytearray()
    for name, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += str(value).encode("utf-8")
        body += b"\r\n"
    for name, (filename, content, content_type) in files.items():
        body += f"--{boundary}\r\n".encode()
        body += (
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
        ).encode()
        body += f"Content-Type: {content_type}\r\n\r\n".encode()
        body += content
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        url,
        data=bytes(body),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def get_url(url):
    """GET an arbitrary URL; return (status, body)."""
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def post(data):
    return post_form(POST_URL, data)


def delete(data):
    return post_form(DELETE_URL, data)


def patch(data):
    return post_form(PATCH_URL, data)


def login(email, password):
    return post_form(LOGIN_URL, {"email": email, "password": password})


def logout():
    return post_form(LOGOUT_URL, {})


def post_with_file(fields, files):
    return post_multipart(POST_URL, fields, files)


def patch_with_file(fields, files):
    return post_multipart(PATCH_URL, fields, files)


# A tiny valid SVG (~120 bytes) — well under the 64KB cap.
TINY_SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
    b'<rect width="10" height="10" fill="#000"/></svg>'
)


def get(user_id):
    """GET /users/get.php?id=...; return (status, body_dict)."""
    return get_url(f"{GET_URL}?id={urllib.parse.quote(str(user_id))}")


def get_all(query=None):
    """GET /users/get_all.php; return (status, body_list)."""
    url = GET_ALL_URL
    if query is not None:
        url = f"{GET_ALL_URL}?query={urllib.parse.quote(str(query))}"
    return get_url(url)


def clear_cookies():
    """Drop all cookies — used to simulate a logged-out client."""
    COOKIE_JAR.clear()


def assert_eq(label, actual, expected):
    ok = actual == expected
    mark = "OK " if ok else "FAIL"
    print(f"  [{mark}] {label}: got {actual!r}")
    if not ok:
        print(f"        expected {expected!r}")
    return ok


def main():
    results = []

    # ---------- Phase A: unauthenticated tests (registration is public) ----------

    # 1. Missing required fields
    print("=== 1. Missing required fields ===")
    status, body = post({})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "missing_required_fields"))
    results.append(assert_eq(
        "fields",
        sorted(body.get("fields", [])),
        ["email", "name", "password"],
    ))

    # 2. Invalid email
    print("=== 2. Invalid email ===")
    status, body = post({
        "name": "Test",
        "email": "not-an-email",
        "password": "secret",
    })
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_email"))

    # 3. Invalid graduation_year
    print("=== 3. Invalid graduation_year ===")
    status, body = post({
        "name": "Test",
        "email": "valid@example.com",
        "password": "secret",
        "graduation_year": "1500",
    })
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_graduation_year"))

    # 4. Email already taken (seeded user 1)
    print("=== 4. Email already taken (seeded user 1) ===")
    status, body = post({
        "name": "Test",
        "email": "thomasjonathan@example.net",
        "password": "secret",
    })
    results.append(assert_eq("status", status, 409))
    results.append(assert_eq("error", body.get("error"), "email_already_registered"))

    # ---------- Phase B: auth-gate checks (no session yet) ----------

    # A1. Auth gate: GET /users/get.php without session → 401
    print("=== A1. GET without session → 401 ===")
    status, body = get(1)
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # A2. Auth gate: GET /users/get_all.php without session → 401
    print("=== A2. GET ALL without session → 401 ===")
    status, body = get_all()
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # A3. Auth gate: POST /users/patch.php without session → 401
    print("=== A3. PATCH without session → 401 ===")
    status, body = patch({"id": "1", "name": "Anything"})
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # A4. Auth gate: POST /users/delete.php without session → 401
    print("=== A4. DELETE without session → 401 ===")
    status, body = delete({"id": "1"})
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # A5. Logout with no session → 401 not_logged_in
    print("=== A5. logout without session → 401 ===")
    status, body = logout()
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # A6. Login with bad credentials → 401 invalid_credentials
    print("=== A6. login with bad password → 401 ===")
    status, body = login("thomasjonathan@example.net", "definitely-wrong-pw")
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "invalid_credentials"))

    # A7. Login with missing fields → 400 missing_required_fields
    print("=== A7. login with missing fields ===")
    status, body = post_form(LOGIN_URL, {})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "missing_required_fields"))

    # ---------- Phase C: register + login a test account ----------

    print("=== Setup. Register + login test account ===")
    test_email = f"runner.{int(time.time())}.{uuid.uuid4().hex[:8]}@example.com"
    test_password = "test-pw-" + uuid.uuid4().hex
    status, body = post({
        "name": "Test Runner",
        "email": test_email,
        "password": test_password,
    })
    results.append(assert_eq("setup register status", status, 201))
    runner_id = body.get("id")
    if not isinstance(runner_id, int):
        print("FATAL: could not register the test runner account; aborting.")
        sys.exit(1)

    status, body = login(test_email, test_password)
    results.append(assert_eq("setup login status", status, 200))
    results.append(assert_eq("setup login flag", body.get("logged_in"), True))
    results.append(assert_eq("setup login id", body.get("id"), runner_id))

    # ---------- Phase D: gated tests, run with the session cookie ----------

    # 5. Successful create (string profile_picture is ignored — uploads only)
    print("=== 5. Successful create ===")
    unique_email = f"jane.doe.{int(time.time())}@example.com"
    status, body = post({
        "name": "Jane Doe",
        "email": unique_email,
        "password": "hunter2",
        "graduation_year": "2024",
        "field_of_study": "Computer Science",
        "company": "TestCo",
        "profile_picture": "user42.svg",
    })
    results.append(assert_eq("status", status, 201))
    new_id = body.get("id")
    results.append(assert_eq("id type", type(new_id).__name__, "int"))
    if not isinstance(new_id, int):
        print("  Skipping round-trip — no id returned.")
    else:
        # 6. Round-trip: GET the new user
        print(f"=== 6. Round-trip GET id={new_id} ===")
        status, body = get(new_id)
        results.append(assert_eq("status", status, 200))
        results.append(assert_eq("id", body.get("id"), new_id))
        results.append(assert_eq("name", body.get("name"), "Jane Doe"))
        results.append(assert_eq("email", body.get("email"), unique_email))
        results.append(assert_eq("graduation_year", body.get("graduation_year"), 2024))
        results.append(assert_eq("field_of_study", body.get("field_of_study"), "Computer Science"))
        results.append(assert_eq("company", body.get("company"), "TestCo"))
        results.append(assert_eq("current_role", body.get("current_role"), None))
        results.append(assert_eq("location", body.get("location"), None))
        results.append(assert_eq("bio", body.get("bio"), None))
        # No file was uploaded — string field is ignored, so column is null.
        results.append(assert_eq("profile_picture", body.get("profile_picture"), None))
        delete({"id": str(new_id)})

    # 7. GET unknown id → 404
    print("=== 7. GET nonexistent id ===")
    status, body = get(999999)
    results.append(assert_eq("status", status, 404))
    results.append(assert_eq("error", body.get("error"), "user_not_found"))

    # 8. GET invalid id → 400
    print("=== 8. GET invalid id (negative) ===")
    status, body = get(-1)
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 8a. GET ALL — basic shape and content checks
    print("=== 8a. GET ALL ===")
    status, body = get_all()
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("type is list", isinstance(body, list), True))
    if isinstance(body, list):
        results.append(assert_eq(
            "at least 100 seeded users",
            len(body) >= 100,
            True,
        ))
        if body:
            first = body[0]
            results.append(assert_eq("first row is dict", isinstance(first, dict), True))
            # Check expected keys exist
            expected_keys = {
                "id", "name", "email", "graduation_year", "field_of_study",
                "current_role", "company", "location", "bio", "profile_picture",
            }
            results.append(assert_eq(
                "first row has expected keys",
                expected_keys.issubset(first.keys()),
                True,
            ))
            # password_hash should NOT be exposed
            results.append(assert_eq(
                "password_hash not exposed",
                "password_hash" not in first,
                True,
            ))
            # Ordered by id ascending
            ids = [u["id"] for u in body if "id" in u]
            results.append(assert_eq(
                "users ordered by id ascending",
                ids == sorted(ids),
                True,
            ))
            # First seeded user matches CSV row 1
            seeded = next((u for u in body if u.get("id") == 1), None)
            if seeded:
                results.append(assert_eq("seeded user 1 name", seeded.get("name"), "Duane Cruz"))
                results.append(assert_eq(
                    "seeded user 1 profile_picture prefixed",
                    seeded.get("profile_picture"),
                    "/uploads/user1.svg",
                ))

    # 8b. GET ALL with query → substring match against email
    print("=== 8b. GET ALL ?query=<email substring> ===")
    status, body = get_all(query="thomasjonathan")
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("type is list", isinstance(body, list), True))
    if isinstance(body, list):
        results.append(assert_eq("at least one match", len(body) >= 1, True))
        emails = [u.get("email", "") for u in body]
        results.append(assert_eq(
            "every result email contains query",
            all("thomasjonathan" in e for e in emails),
            True,
        ))

    # 8b-2. GET ALL with query that matches nothing → []
    print("=== 8b-2. GET ALL ?query=<no matches> ===")
    status, body = get_all(query="zzz_no_such_email_substring_zzz")
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("body", body, []))

    # 8c. GET ALL with empty query → falls back to returning all
    print("=== 8c. GET ALL ?query= (empty) ===")
    status, body = get_all(query="")
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("type is list", isinstance(body, list), True))
    if isinstance(body, list):
        results.append(assert_eq("at least 100 users", len(body) >= 100, True))

    # 9. DELETE missing id
    print("=== 9. DELETE missing id ===")
    status, body = delete({})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 10. DELETE non-numeric id
    print("=== 10. DELETE non-numeric id ===")
    status, body = delete({"id": "abc"})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 11. DELETE negative id
    print("=== 11. DELETE negative id ===")
    status, body = delete({"id": "-5"})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 12. DELETE nonexistent id
    print("=== 12. DELETE nonexistent id ===")
    status, body = delete({"id": "999999"})
    results.append(assert_eq("status", status, 404))
    results.append(assert_eq("error", body.get("error"), "user_not_found"))

    # 13. Create-then-delete round trip
    print("=== 13. Create-then-delete round trip ===")
    unique_email = f"to.delete.{int(time.time())}@example.com"
    status, body = post({
        "name": "To Delete",
        "email": unique_email,
        "password": "secret",
    })
    results.append(assert_eq("create status", status, 201))
    target_id = body.get("id")
    if isinstance(target_id, int):
        # Confirm it exists
        status, body = get(target_id)
        results.append(assert_eq("pre-delete GET status", status, 200))
        results.append(assert_eq("pre-delete GET id", body.get("id"), target_id))

        # Delete it
        status, body = delete({"id": str(target_id)})
        results.append(assert_eq("delete status", status, 200))
        results.append(assert_eq("deleted id", body.get("deleted"), target_id))

        # Confirm it's gone
        status, body = get(target_id)
        results.append(assert_eq("post-delete GET status", status, 404))
        results.append(assert_eq("post-delete GET error", body.get("error"), "user_not_found"))

        # Deleting again → 404
        status, body = delete({"id": str(target_id)})
        results.append(assert_eq("re-delete status", status, 404))
        results.append(assert_eq("re-delete error", body.get("error"), "user_not_found"))
    else:
        print("  Skipping delete round-trip — create did not return an id.")

    # 14. PATCH missing id
    print("=== 14. PATCH missing id ===")
    status, body = patch({"name": "Anything"})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 15. PATCH invalid id
    print("=== 15. PATCH invalid id ===")
    status, body = patch({"id": "abc", "name": "Anything"})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 16. PATCH nonexistent id
    print("=== 16. PATCH nonexistent id ===")
    status, body = patch({"id": "999999", "name": "Ghost"})
    results.append(assert_eq("status", status, 404))
    results.append(assert_eq("error", body.get("error"), "user_not_found"))

    # 17. PATCH with no fields supplied
    print("=== 17. PATCH no fields to update ===")
    status, body = patch({"id": "1"})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "no_fields_to_update"))

    # 18. PATCH with invalid email
    print("=== 18. PATCH invalid email ===")
    status, body = patch({"id": "1", "email": "not-an-email"})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_email"))

    # 19. PATCH with invalid graduation_year
    print("=== 19. PATCH invalid graduation_year ===")
    status, body = patch({"id": "1", "graduation_year": "1500"})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_graduation_year"))

    # 20. Create-patch-verify round trip
    print("=== 20. Create-patch-verify round trip ===")
    unique_email = f"to.patch.{int(time.time())}@example.com"
    status, body = post({
        "name": "Original Name",
        "email": unique_email,
        "password": "secret",
        "company": "OldCo",
    })
    results.append(assert_eq("create status", status, 201))
    patch_id = body.get("id")
    if isinstance(patch_id, int):
        # Patch a few fields
        status, body = patch({
            "id": str(patch_id),
            "name": "New Name",
            "company": "NewCo",
            "location": "Berlin",
        })
        results.append(assert_eq("patch status", status, 200))
        results.append(assert_eq("updated id", body.get("updated"), patch_id))

        # Verify changes
        status, body = get(patch_id)
        results.append(assert_eq("post-patch name", body.get("name"), "New Name"))
        results.append(assert_eq("post-patch company", body.get("company"), "NewCo"))
        results.append(assert_eq("post-patch location", body.get("location"), "Berlin"))
        # Email was not patched, should remain
        results.append(assert_eq("post-patch email unchanged", body.get("email"), unique_email))

        # 21. PATCH email conflict (try to set to seeded user 1's email)
        print("=== 21. PATCH email conflict ===")
        status, body = patch({
            "id": str(patch_id),
            "email": "thomasjonathan@example.net",
        })
        results.append(assert_eq("status", status, 409))
        results.append(assert_eq("error", body.get("error"), "email_already_registered"))

        # Cleanup
        delete({"id": str(patch_id)})
    else:
        print("  Skipping patch round-trip — create did not return an id.")

    # 22. POST with valid image upload
    print("=== 22. POST with valid SVG upload ===")
    unique_email = f"upload.ok.{int(time.time())}@example.com"
    status, body = post_with_file(
        {
            "name": "Upload OK",
            "email": unique_email,
            "password": "secret",
        },
        {"profile_picture": ("avatar.svg", TINY_SVG, "image/svg+xml")},
    )
    results.append(assert_eq("create status", status, 201))
    upload_id = body.get("id")
    if isinstance(upload_id, int):
        status, body = get(upload_id)
        results.append(assert_eq("get status", status, 200))
        pic = body.get("profile_picture", "")
        results.append(assert_eq("picture is path", pic.startswith("/uploads/"), True))
        results.append(assert_eq("picture has .svg ext", pic.endswith(".svg"), True))
        # UUID-shaped name (8-4-4-4-12 hex)
        filename = pic.rsplit("/", 1)[-1]
        results.append(assert_eq(
            "filename is uuid.svg",
            len(filename) == 32 + 4 + 4,  # 32 hex + 4 dashes + ".svg"
            True,
        ))
        delete({"id": str(upload_id)})
    else:
        print("  Skipping upload verification — no id returned.")

    # 23. POST with invalid file type
    print("=== 23. POST with invalid file type ===")
    unique_email = f"upload.bad.{int(time.time())}@example.com"
    status, body = post_with_file(
        {
            "name": "Bad Upload",
            "email": unique_email,
            "password": "secret",
        },
        {"profile_picture": ("evil.txt", b"not an image", "text/plain")},
    )
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_file_type"))

    # 24. POST with file too large (exceed 64KB cap)
    print("=== 24. POST with oversized file ===")
    unique_email = f"upload.big.{int(time.time())}@example.com"
    big_payload = b"X" * (70 * 1024)  # 70KB > 64KB
    status, body = post_with_file(
        {
            "name": "Big Upload",
            "email": unique_email,
            "password": "secret",
        },
        {"profile_picture": ("big.jpg", big_payload, "image/jpeg")},
    )
    # PHP enforces upload_max_filesize at the transport layer; either way
    # the API surfaces it as a 400 with file_too_large.
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "file_too_large"))

    # 25. PATCH with new picture replaces the old one
    print("=== 25. PATCH replaces profile picture ===")
    unique_email = f"upload.patch.{int(time.time())}@example.com"
    status, body = post_with_file(
        {"name": "Patch Pic", "email": unique_email, "password": "secret"},
        {"profile_picture": ("first.svg", TINY_SVG, "image/svg+xml")},
    )
    results.append(assert_eq("create status", status, 201))
    pp_id = body.get("id")
    if isinstance(pp_id, int):
        status, body = get(pp_id)
        first_pic = body.get("profile_picture")
        results.append(assert_eq("first pic set", isinstance(first_pic, str), True))

        # Patch with a new file
        status, body = patch_with_file(
            {"id": str(pp_id)},
            {"profile_picture": ("second.svg", TINY_SVG, "image/svg+xml")},
        )
        results.append(assert_eq("patch status", status, 200))

        status, body = get(pp_id)
        second_pic = body.get("profile_picture")
        results.append(assert_eq("second pic set", isinstance(second_pic, str), True))
        results.append(assert_eq("filename changed", first_pic != second_pic, True))

        delete({"id": str(pp_id)})
    else:
        print("  Skipping patch-replace — no id returned.")

    # 26. PATCH with only a file (no other fields) — must succeed
    print("=== 26. PATCH with only a file ===")
    unique_email = f"upload.fileonly.{int(time.time())}@example.com"
    status, body = post({
        "name": "File Only Patch",
        "email": unique_email,
        "password": "secret",
    })
    fo_id = body.get("id")
    if isinstance(fo_id, int):
        status, body = patch_with_file(
            {"id": str(fo_id)},
            {"profile_picture": ("only.svg", TINY_SVG, "image/svg+xml")},
        )
        results.append(assert_eq("status", status, 200))
        results.append(assert_eq("updated id", body.get("updated"), fo_id))
        delete({"id": str(fo_id)})
    else:
        print("  Skipping file-only patch — no id returned.")

    # ---------- Phase E: logout tests + cleanup ----------

    # L1. Logout while logged in → 200 logged_out
    print("=== L1. logout while logged in ===")
    status, body = logout()
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("logged_out id", body.get("logged_out"), runner_id))

    # L2. After logout, gated endpoint goes back to 401
    print("=== L2. GET after logout → 401 ===")
    status, body = get(1)
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # Cleanup: log back in to delete the runner account. Self-deletion is
    # expected to clear the server-side session as a side-effect — verify
    # that a follow-up gated request returns 401 without us having to call
    # logout() explicitly.
    print("=== Cleanup. log back in + delete runner ===")
    status, body = login(test_email, test_password)
    results.append(assert_eq("cleanup login status", status, 200))
    status, body = delete({"id": str(runner_id)})
    results.append(assert_eq("cleanup delete status", status, 200))

    print("=== L3. self-delete cleared the session → 401 ===")
    status, body = get(1)
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    print()
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"{passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
