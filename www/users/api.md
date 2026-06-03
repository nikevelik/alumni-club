# Users API

## GET /users/get.php

Returns a single user by ID.

**Query Parameters**

| Parameter | Type    | Required | Description                                |
|-----------|---------|----------|--------------------------------------------|
| id        | integer | yes      | The user's ID (must be a positive integer) |

**Response**

`200 OK` — user object:

```json
{
  "id": 1,
  "name": "Duane Cruz",
  "email": "thomasjonathan@example.net",
  "graduation_year": 2010,
  "field_of_study": "Psychology",
  "current_role": "Accountant",
  "company": "InnovateX",
  "location": "Rebeccaville",
  "bio": "Feeling start grow magazine task candidate early.",
  "profile_picture": "/uploads/user1.svg"
}
```

`400 Bad Request` — id missing, non-numeric, or non-positive:

```json
{ "error": "invalid_id" }
```

`404 Not Found` — no user with that id:

```json
{ "error": "user_not_found" }
```

---

## GET /users/get_all.php

Returns all users, ordered by id. Optionally accepts a `query` parameter that
filters users whose `email` contains the query as a substring (case-insensitive,
matching the column collation).

**Query Parameters**

| Parameter | Type   | Required | Description                                          |
|-----------|--------|----------|------------------------------------------------------|
| query     | string | no       | Substring match against `email`. When omitted or empty, all users are returned. |

**Response**

`200 OK` — array of user objects (same shape as `/users/get.php`):

```json
[
  {
    "id": 1,
    "name": "Duane Cruz",
    "email": "thomasjonathan@example.net",
    "graduation_year": 2010,
    "field_of_study": "Psychology",
    "current_role": "Accountant",
    "company": "InnovateX",
    "location": "Rebeccaville",
    "bio": "Feeling start grow magazine task candidate early.",
    "profile_picture": "/uploads/user1.svg"
  }
]
```

If there are no users, returns `[]`.

**Example**

```bash
curl http://35.208.59.90/users/get_all.php
```

---

## POST /users/post.php

Creates a new user (registration). Accepts `application/x-www-form-urlencoded` or
`multipart/form-data` (i.e. `$_POST`). Use `multipart/form-data` if uploading a
profile picture.

**Body Parameters**

| Parameter        | Type    | Required | Description                            |
|------------------|---------|----------|----------------------------------------|
| name             | string  | yes      | Display name                           |
| email            | string  | yes      | Must be a valid email, unique          |
| password         | string  | yes      | Plain password; hashed server-side     |
| graduation_year  | integer | no       | Between 1900 and 2100                  |
| field_of_study   | string  | no       |                                        |
| current_role     | string  | no       |                                        |
| company          | string  | no       |                                        |
| location         | string  | no       |                                        |
| bio              | string  | no       |                                        |
| profile_picture  | file    | no       | Image file (jpg/png/gif/webp/svg, max 64KB). Server stores it under `/uploads/{uuid}.{ext}`. |

**Responses**

`201 Created` — success:

```json
{ "id": 101 }
```

`400 Bad Request` — missing required fields:

```json
{ "error": "missing_required_fields", "fields": ["email", "password"] }
```

`400 Bad Request` — invalid email format:

```json
{ "error": "invalid_email" }
```

`400 Bad Request` — graduation year out of range:

```json
{ "error": "invalid_graduation_year" }
```

`400 Bad Request` — uploaded file too large (over 64KB):

```json
{ "error": "file_too_large" }
```

`400 Bad Request` — uploaded file is not an allowed image type:

```json
{ "error": "invalid_file_type" }
```

`400 Bad Request` — generic upload failure (transport / move error):

```json
{ "error": "upload_failed" }
```

`409 Conflict` — email already in use:

```json
{ "error": "email_already_registered" }
```

**Example**

```bash
curl -X POST http://35.208.59.90/users/post.php \
  -F "name=Jane Doe" \
  -F "email=jane@example.com" \
  -F "password=hunter2" \
  -F "graduation_year=2024" \
  -F "profile_picture=@./avatar.jpg"
```

**Notes**

- Passwords are hashed with SHA-256 to match the seeded data format. For production,
  switch to `password_hash()` / `password_verify()` (bcrypt).

---

## POST /users/delete.php

Deletes a user by ID. Hard delete — the row is removed from the `users` table.

**Body Parameters**

| Parameter | Type    | Required | Description                                |
|-----------|---------|----------|--------------------------------------------|
| id        | integer | yes      | The user's ID (must be a positive integer) |

**Responses**

`200 OK` — success:

```json
{ "deleted": 101 }
```

`400 Bad Request` — id missing, non-numeric, or non-positive:

```json
{ "error": "invalid_id" }
```

`404 Not Found` — no user with that id:

```json
{ "error": "user_not_found" }
```

**Example**

```bash
curl -X POST http://35.208.59.90/users/delete.php -d "id=101"
```

---

## POST /users/patch.php

Partially updates an existing user. Only fields that are present and non-empty in
the request are written; missing or empty fields are left unchanged. Use
`multipart/form-data` if uploading a new profile picture.

**Body Parameters**

| Parameter        | Type    | Required | Description                            |
|------------------|---------|----------|----------------------------------------|
| id               | integer | yes      | The user's ID (must be a positive integer) |
| name             | string  | no       | New display name                       |
| email            | string  | no       | Must be valid and unique               |
| password         | string  | no       | Plain password; hashed server-side     |
| graduation_year  | integer | no       | Between 1900 and 2100                  |
| field_of_study   | string  | no       |                                        |
| current_role     | string  | no       |                                        |
| company          | string  | no       |                                        |
| location         | string  | no       |                                        |
| bio              | string  | no       |                                        |
| profile_picture  | file    | no       | Image file (jpg/png/gif/webp/svg, max 64KB). Replaces the previous picture; the old file is deleted from disk. |

At least one updatable field (or a new picture) must be supplied alongside `id`.

**Responses**

`200 OK` — success:

```json
{ "updated": 101 }
```

`400 Bad Request` — id missing/invalid, no fields supplied, invalid email, invalid year, or upload errors:

```json
{ "error": "invalid_id" }
{ "error": "no_fields_to_update" }
{ "error": "invalid_email" }
{ "error": "invalid_graduation_year" }
{ "error": "file_too_large" }
{ "error": "invalid_file_type" }
{ "error": "upload_failed" }
```

`404 Not Found` — no user with that id:

```json
{ "error": "user_not_found" }
```

`409 Conflict` — email already used by a different user:

```json
{ "error": "email_already_registered" }
```

**Example**

```bash
curl -X POST http://35.208.59.90/users/patch.php \
  -F "id=101" \
  -F "company=NewCo" \
  -F "location=Berlin" \
  -F "profile_picture=@./new-avatar.png"
```

---

## POST /users/login.php

Authenticates a user and starts a PHP session. The session id is set in the
`PHPSESSID` cookie (`HttpOnly`, `SameSite=Lax`, `Secure` over HTTPS). Subsequent
endpoints that read `$_SESSION['user_id']` will see the logged-in user.

**Body Parameters**

| Parameter | Type   | Required | Description                  |
|-----------|--------|----------|------------------------------|
| email     | string | yes      | The user's email             |
| password  | string | yes      | Plain password (hashed server-side and compared) |

**Responses**

`200 OK` — success. The session cookie is set on the response:

```json
{ "id": 101, "logged_in": true }
```

`400 Bad Request` — missing required fields:

```json
{ "error": "missing_required_fields", "fields": ["email", "password"] }
```

`401 Unauthorized` — email not found or password mismatch (single error code,
no enumeration):

```json
{ "error": "invalid_credentials" }
```

**Example**

```bash
curl -c cookies.txt -X POST http://35.208.59.90/users/login.php \
  -d "email=jane@example.com" \
  -d "password=hunter2"
```

---

## POST /users/logout.php

Clears the current PHP session and expires the session cookie. The current
user id is read from `$_SESSION['user_id']`; no body parameters are required.

**Responses**

`200 OK` — success:

```json
{ "logged_out": 101 }
```

`401 Unauthorized` — no active session:

```json
{ "error": "not_logged_in" }
```

**Example**

```bash
curl -b cookies.txt -X POST http://35.208.59.90/users/logout.php
```
