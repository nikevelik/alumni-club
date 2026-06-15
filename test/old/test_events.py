#!/usr/bin/env python3
"""
End-to-end tests for the /events/ endpoints.
Run: python3 test_events.py

Auth model: every events endpoint is gated behind a session cookie. Tests
register a throwaway account via /users/post.php (which is public), log in
via /users/login.php, and run all event assertions through that authenticated
session. The cookie is held in a CookieJar bound to the global opener so
urlopen() carries it on every request automatically.
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
GET_URL       = f"{BASE_URL}/events/get.php"
GET_ALL_URL   = f"{BASE_URL}/events/get_all.php"
POST_URL      = f"{BASE_URL}/events/post.php"
DELETE_URL    = f"{BASE_URL}/events/delete.php"
USERS_POST    = f"{BASE_URL}/users/post.php"
USERS_DELETE  = f"{BASE_URL}/users/delete.php"
LOGIN_URL     = f"{BASE_URL}/users/login.php"
LOGOUT_URL    = f"{BASE_URL}/users/logout.php"

# Seeded user 1 — used as the creator for test events. Note that with auth
# in place, the *requester* is the logged-in test runner; the `creator` field
# is a separate parameter that just has to reference an existing user row.
SEEDED_CREATOR_ID = 1


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


def login(email, password):
    return post_form(LOGIN_URL, {"email": email, "password": password})


def logout():
    return post_form(LOGOUT_URL, {})


def get(event_id):
    """GET /events/get.php?id=...; return (status, body_dict)."""
    return get_url(f"{GET_URL}?id={urllib.parse.quote(str(event_id))}")


def get_all(query=None):
    """GET /events/get_all.php; return (status, body_list)."""
    url = GET_ALL_URL
    if query is not None:
        url = f"{GET_ALL_URL}?query={urllib.parse.quote(str(query))}"
    return get_url(url)


def assert_eq(label, actual, expected):
    ok = actual == expected
    mark = "OK " if ok else "FAIL"
    print(f"  [{mark}] {label}: got {actual!r}")
    if not ok:
        print(f"        expected {expected!r}")
    return ok


def main():
    results = []

    # ---------- Phase A: auth-gate checks (no session yet) ----------

    # A1. GET /events/get.php without session → 401
    print("=== A1. GET without session → 401 ===")
    status, body = get(1)
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # A2. GET /events/get_all.php without session → 401
    print("=== A2. GET ALL without session → 401 ===")
    status, body = get_all()
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # A3. POST /events/post.php without session → 401
    print("=== A3. POST without session → 401 ===")
    status, body = post({
        "date": "2026-09-15",
        "name": "Should Not Pass",
        "creator": str(SEEDED_CREATOR_ID),
    })
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # A4. POST /events/delete.php without session → 401
    print("=== A4. DELETE without session → 401 ===")
    status, body = delete({"id": "1"})
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # ---------- Phase B: register + login a test runner ----------

    print("=== Setup. Register + login test runner ===")
    test_email = f"events.runner.{int(time.time())}.{uuid.uuid4().hex[:8]}@example.com"
    test_password = "test-pw-" + uuid.uuid4().hex
    status, body = post_form(USERS_POST, {
        "name": "Events Test Runner",
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

    # ---------- Phase C: gated tests, run with the session cookie ----------

    # 1. Missing required fields
    print("=== 1. Missing required fields ===")
    status, body = post({})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "missing_required_fields"))
    results.append(assert_eq(
        "fields",
        sorted(body.get("fields", [])),
        ["creator", "date", "name"],
    ))

    # 2. Invalid date
    print("=== 2. Invalid date ===")
    status, body = post({
        "date": "not-a-date",
        "name": "Test Event",
        "creator": str(SEEDED_CREATOR_ID),
    })
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_date"))

    # 3. Invalid creator (non-numeric)
    print("=== 3. Invalid creator ===")
    status, body = post({
        "date": "2026-09-15",
        "name": "Test Event",
        "creator": "abc",
    })
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_creator"))

    # 4. Creator does not exist
    print("=== 4. Creator does not exist ===")
    status, body = post({
        "date": "2026-09-15",
        "name": "Test Event",
        "creator": "999999",
    })
    results.append(assert_eq("status", status, 404))
    results.append(assert_eq("error", body.get("error"), "creator_not_found"))

    # 5. Successful create
    print("=== 5. Successful create ===")
    unique_name = f"Test Event {int(time.time())}"
    status, body = post({
        "date": "2026-09-15",
        "name": unique_name,
        "details": "Catered dinner, networking, awards ceremony.",
        "creator": str(SEEDED_CREATOR_ID),
    })
    results.append(assert_eq("status", status, 201))
    new_id = body.get("id")
    results.append(assert_eq("id type", type(new_id).__name__, "int"))
    if not isinstance(new_id, int):
        print("  Skipping round-trip — no id returned.")
    else:
        # 6. Round-trip: GET the new event
        print(f"=== 6. Round-trip GET id={new_id} ===")
        status, body = get(new_id)
        results.append(assert_eq("status", status, 200))
        results.append(assert_eq("id", body.get("id"), new_id))
        results.append(assert_eq("date", body.get("date"), "2026-09-15"))
        results.append(assert_eq("name", body.get("name"), unique_name))
        results.append(assert_eq(
            "details",
            body.get("details"),
            "Catered dinner, networking, awards ceremony.",
        ))
        results.append(assert_eq("creator", body.get("creator"), SEEDED_CREATOR_ID))

        # Cleanup so reruns don't accumulate rows.
        delete({"id": str(new_id)})

    # 7. Create with no details (optional field omitted)
    print("=== 7. Create with no details ===")
    bare_name = f"Bare Event {int(time.time())}"
    status, body = post({
        "date": "2026-12-31",
        "name": bare_name,
        "creator": str(SEEDED_CREATOR_ID),
    })
    results.append(assert_eq("status", status, 201))
    bare_id = body.get("id")
    if isinstance(bare_id, int):
        status, body = get(bare_id)
        results.append(assert_eq("status", status, 200))
        results.append(assert_eq("details defaults to None", body.get("details"), None))
        delete({"id": str(bare_id)})

    # 8. GET unknown id → 404
    print("=== 8. GET nonexistent id ===")
    status, body = get(999999)
    results.append(assert_eq("status", status, 404))
    results.append(assert_eq("error", body.get("error"), "event_not_found"))

    # 9. GET invalid id → 400
    print("=== 9. GET invalid id (negative) ===")
    status, body = get(-1)
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 10. GET ALL — basic shape
    print("=== 10. GET ALL ===")
    status, body = get_all()
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("type is list", isinstance(body, list), True))
    if isinstance(body, list) and body:
        results.append(assert_eq("at least 3 seeded events", len(body) >= 3, True))
        first = body[0]
        results.append(assert_eq("first row is dict", isinstance(first, dict), True))
        expected_keys = {"id", "date", "name", "details", "creator"}
        results.append(assert_eq(
            "first row has expected keys",
            expected_keys.issubset(first.keys()),
            True,
        ))
        ids = [e["id"] for e in body if "id" in e]
        results.append(assert_eq(
            "events ordered by id ascending",
            ids == sorted(ids),
            True,
        ))
        # Seeded event 1 from events.csv
        seeded = next((e for e in body if e.get("id") == 1), None)
        if seeded:
            results.append(assert_eq("seeded event 1 name", seeded.get("name"), "Annual Alumni Reunion"))
            results.append(assert_eq("seeded event 1 date", seeded.get("date"), "2026-09-15"))
            results.append(assert_eq("seeded event 1 creator", seeded.get("creator"), 1))

    # 11. GET ALL with query → substring match against name
    print("=== 11. GET ALL ?query=<name substring> ===")
    needle = f"Searchable {int(time.time())}"
    status, body = post({
        "date": "2026-09-15",
        "name": needle,
        "creator": str(SEEDED_CREATOR_ID),
    })
    results.append(assert_eq("create status", status, 201))
    needle_id = body.get("id")
    status, body = get_all(query=needle)
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("type is list", isinstance(body, list), True))
    if isinstance(body, list):
        results.append(assert_eq("at least one match", len(body) >= 1, True))
        names = [e.get("name", "") for e in body]
        results.append(assert_eq(
            "every result name contains query",
            all(needle in n for n in names),
            True,
        ))
    if isinstance(needle_id, int):
        delete({"id": str(needle_id)})

    # 11b. GET ALL with query that matches nothing → []
    print("=== 11b. GET ALL ?query=<no matches> ===")
    status, body = get_all(query="zzz_no_such_event_substring_zzz")
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("body", body, []))

    # 11c. GET ALL with empty query → falls back to returning all
    print("=== 11c. GET ALL ?query= (empty) ===")
    status, body = get_all(query="")
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("type is list", isinstance(body, list), True))

    # 12. DELETE missing id
    print("=== 12. DELETE missing id ===")
    status, body = delete({})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 13. DELETE non-numeric id
    print("=== 13. DELETE non-numeric id ===")
    status, body = delete({"id": "abc"})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 14. DELETE negative id
    print("=== 14. DELETE negative id ===")
    status, body = delete({"id": "-5"})
    results.append(assert_eq("status", status, 400))
    results.append(assert_eq("error", body.get("error"), "invalid_id"))

    # 15. DELETE nonexistent id
    print("=== 15. DELETE nonexistent id ===")
    status, body = delete({"id": "999999"})
    results.append(assert_eq("status", status, 404))
    results.append(assert_eq("error", body.get("error"), "event_not_found"))

    # 16. Create-then-delete round trip
    print("=== 16. Create-then-delete round trip ===")
    status, body = post({
        "date": "2026-09-15",
        "name": f"To Delete {int(time.time())}",
        "creator": str(SEEDED_CREATOR_ID),
    })
    results.append(assert_eq("create status", status, 201))
    target_id = body.get("id")
    if isinstance(target_id, int):
        status, body = get(target_id)
        results.append(assert_eq("pre-delete GET status", status, 200))
        results.append(assert_eq("pre-delete GET id", body.get("id"), target_id))

        status, body = delete({"id": str(target_id)})
        results.append(assert_eq("delete status", status, 200))
        results.append(assert_eq("deleted id", body.get("deleted"), target_id))

        status, body = get(target_id)
        results.append(assert_eq("post-delete GET status", status, 404))
        results.append(assert_eq("post-delete GET error", body.get("error"), "event_not_found"))

        status, body = delete({"id": str(target_id)})
        results.append(assert_eq("re-delete status", status, 404))
        results.append(assert_eq("re-delete error", body.get("error"), "event_not_found"))
    else:
        print("  Skipping delete round-trip — create did not return an id.")

    # ---------- Phase D: post-logout gate check + cleanup ----------

    # L1. Logout → 200
    print("=== L1. logout while logged in ===")
    status, body = logout()
    results.append(assert_eq("status", status, 200))
    results.append(assert_eq("logged_out id", body.get("logged_out"), runner_id))

    # L2. After logout, an events endpoint goes back to 401
    print("=== L2. GET ALL after logout → 401 ===")
    status, body = get_all()
    results.append(assert_eq("status", status, 401))
    results.append(assert_eq("error", body.get("error"), "not_logged_in"))

    # Cleanup: log back in and delete the runner account.
    print("=== Cleanup. log back in + delete runner ===")
    status, body = login(test_email, test_password)
    results.append(assert_eq("cleanup login status", status, 200))
    status, body = post_form(USERS_DELETE, {"id": str(runner_id)})
    results.append(assert_eq("cleanup delete status", status, 200))

    print()
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"{passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
