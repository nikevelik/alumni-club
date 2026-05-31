#!/usr/bin/env python3
"""
End-to-end tests for the /users/ endpoints.
Run: python3 test_users.py
"""

import time
import urllib.parse
import urllib.request
import json
import sys

BASE_URL = "http://35.208.59.90"
GET_URL = f"{BASE_URL}/users/get.php"
GET_ALL_URL = f"{BASE_URL}/users/get_all.php"
POST_URL = f"{BASE_URL}/users/post.php"
DELETE_URL = f"{BASE_URL}/users/delete.php"
PATCH_URL = f"{BASE_URL}/users/patch.php"


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


def delete(data):
    return post_form(DELETE_URL, data)


def patch(data):
    return post_form(PATCH_URL, data)


def get(user_id):
    """GET /users/get.php?id=...; return (status, body_dict)."""
    url = f"{GET_URL}?id={urllib.parse.quote(str(user_id))}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def get_all(query=None):
    """GET /users/get_all.php; return (status, body_list)."""
    url = GET_ALL_URL
    if query is not None:
        url = f"{GET_ALL_URL}?query={urllib.parse.quote(str(query))}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def assert_eq(label, actual, expected):
    ok = actual == expected
    mark = "OK " if ok else "FAIL"
    print(f"  [{mark}] {label}: got {actual!r}")
    if not ok:
        print(f"        expected {expected!r}")
    return ok


def main():
    results = []

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

    # 5. Successful create
    print("=== 5. Successful create ===")
    unique_email = f"jane.doe.{int(time.time())}@example.com"
    status, body = post({
        "name": "Jane Doe",
        "email": unique_email,
        "password": "hunter2",
        "graduation_year": "2024",
        "field_of_study": "Computer Science",
        "company": "TestCo",
        "profile_picture": "user42.jpg",
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
        results.append(assert_eq("profile_picture", body.get("profile_picture"), "/img/user42.jpg"))

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
                    "/img/user1.jpg",
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

    print()
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"{passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
