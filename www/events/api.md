# Events API

## Authentication

Every endpoint on this API is gated behind a session — the caller must have
logged in via [`POST /users/login.php`](../users/api.md#post-userslogphp) and
must include the resulting `PHPSESSID` cookie in every request. Otherwise the
endpoint short-circuits before reaching any business logic and returns:

`401 Unauthorized`:

```json
{ "error": "not_logged_in" }
```

`curl` users typically hold the cookie in a jar:

```bash
curl -c cookies.txt -X POST http://35.208.59.90/users/login.php -d "email=…" -d "password=…"
curl -b cookies.txt http://35.208.59.90/events/get_all.php
```

---

## GET /events/get.php

Returns a single event by ID.

**Query Parameters**

| Parameter | Type    | Required | Description                                 |
|-----------|---------|----------|---------------------------------------------|
| id        | integer | yes      | The event's ID (must be a positive integer) |

**Response**

`200 OK` — event object:

```json
{
  "id": 1,
  "date": "2026-09-15",
  "name": "Annual Alumni Reunion",
  "details": "Catered dinner, networking, awards ceremony.",
  "creator": 1
}
```

`400 Bad Request` — id missing, non-numeric, or non-positive:

```json
{ "error": "invalid_id" }
```

`404 Not Found` — no event with that id:

```json
{ "error": "event_not_found" }
```

---

## GET /events/get_all.php

Returns all events, ordered by id. Optionally accepts a `query` parameter that
filters events whose `name` contains the query as a substring (case-insensitive,
matching the column collation).

**Query Parameters**

| Parameter | Type   | Required | Description                                          |
|-----------|--------|----------|------------------------------------------------------|
| query     | string | no       | Substring match against `name`. When omitted or empty, all events are returned. |

**Response**

`200 OK` — array of event objects (same shape as `/events/get.php`):

```json
[
  {
    "id": 1,
    "date": "2026-09-15",
    "name": "Annual Alumni Reunion",
    "details": "Catered dinner, networking, awards ceremony.",
    "creator": 1
  }
]
```

If there are no events, returns `[]`.

**Example**

```bash
curl http://35.208.59.90/events/get_all.php
```

---

## POST /events/post.php

Creates a new event. Accepts `application/x-www-form-urlencoded` or
`multipart/form-data` (i.e. `$_POST`). The event's `creator` is taken from the
authenticated session — clients cannot supply or override it.

**Body Parameters**

| Parameter | Type    | Required | Description                                 |
|-----------|---------|----------|---------------------------------------------|
| date      | string  | yes      | Event date in `YYYY-MM-DD` format           |
| name      | string  | yes      | Event name                                  |
| details   | string  | no       | Free-form description                       |

**Responses**

`201 Created` — success:

```json
{ "id": 42 }
```

`400 Bad Request` — missing required fields:

```json
{ "error": "missing_required_fields", "fields": ["date", "name"] }
```

`400 Bad Request` — invalid date format (must be `YYYY-MM-DD`):

```json
{ "error": "invalid_date" }
```

`404 Not Found` — the session's user no longer exists:

```json
{ "error": "creator_not_found" }
```

**Example**

```bash
curl -b cookies.txt -X POST http://35.208.59.90/events/post.php \
  -d "date=2026-09-15" \
  -d "name=Annual Alumni Reunion" \
  -d "details=Catered dinner, networking, awards ceremony."
```

---

## POST /events/delete.php

Deletes an event by ID. Hard delete — the row is removed from the `events` table.

**Body Parameters**

| Parameter | Type    | Required | Description                                 |
|-----------|---------|----------|---------------------------------------------|
| id        | integer | yes      | The event's ID (must be a positive integer) |

**Responses**

`200 OK` — success:

```json
{ "deleted": 42 }
```

`400 Bad Request` — id missing, non-numeric, or non-positive:

```json
{ "error": "invalid_id" }
```

`404 Not Found` — no event with that id:

```json
{ "error": "event_not_found" }
```

**Example**

```bash
curl -X POST http://35.208.59.90/events/delete.php -d "id=42"
```
