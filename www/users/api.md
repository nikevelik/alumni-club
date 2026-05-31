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
  "profile_picture": "/img/user1.jpg"
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
    "profile_picture": "/img/user1.jpg"
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
`multipart/form-data` (i.e. `$_POST`).

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
| profile_picture  | string  | no       | Filename only (e.g. `user42.jpg`)      |

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

`409 Conflict` — email already in use:

```json
{ "error": "email_already_registered" }
```

**Example**

```bash
curl -X POST http://35.208.59.90/users/post.php \
  -d "name=Jane Doe" \
  -d "email=jane@example.com" \
  -d "password=hunter2" \
  -d "graduation_year=2024"
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
the request are written; missing or empty fields are left unchanged.

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
| profile_picture  | string  | no       | Filename only (e.g. `user42.jpg`)      |

At least one updatable field must be supplied alongside `id`.

**Responses**

`200 OK` — success:

```json
{ "updated": 101 }
```

`400 Bad Request` — id missing/invalid, no fields supplied, invalid email, or invalid year:

```json
{ "error": "invalid_id" }
{ "error": "no_fields_to_update" }
{ "error": "invalid_email" }
{ "error": "invalid_graduation_year" }
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
  -d "id=101" \
  -d "company=NewCo" \
  -d "location=Berlin"
```
