# Users API — Minimal Spec

Base: `http://35.208.59.90`  ·  Auth: PHP session cookie (`PHPSESSID`), set by `login.php`.

## Auth matrix

| Endpoint                 | Method | Auth | Purpose                  |
|--------------------------|--------|------|--------------------------|
| `/users/login.php`       | POST   | no   | Start session            |
| `/users/logout.php`      | POST   | yes  | End session              |
| `/users/post.php`        | POST   | no   | Register                 |
| `/users/get.php`         | GET    | yes  | Fetch one user           |
| `/users/get_all.php`     | GET    | yes  | List / search users      |
| `/users/patch.php`       | POST   | yes  | Partial update           |
| `/users/delete.php`      | POST   | yes  | Hard delete              |

Gated endpoints without a session → `401 { "error": "not_logged_in" }`.

## User object

```json
{
  "id": 1, "name": "Duane Cruz", "email": "x@y.net",
  "graduation_year": 2010, "field_of_study": "Psychology",
  "current_role": "Accountant", "company": "InnovateX",
  "location": "Rebeccaville", "bio": "…",
  "profile_picture": "/uploads/user1.svg"
}
```

## POST /users/login.php
- Body: `email`, `password` (form-encoded).
- `200 { "id": N, "logged_in": true }` — sets `PHPSESSID`.
- `400 missing_required_fields` · `401 invalid_credentials`.

## POST /users/logout.php
- No body. Reads `$_SESSION['user_id']`.
- `200 { "logged_out": N }` · `401 not_logged_in`.

## POST /users/post.php (register)
- `application/x-www-form-urlencoded` or `multipart/form-data`.
- Required: `name`, `email`, `password`. Optional: `graduation_year` (1900–2100), `field_of_study`, `current_role`, `company`, `location`, `bio`, `profile_picture` (jpg/png/gif/webp/svg, ≤64KB).
- `201 { "id": N }`.
- `400`: `missing_required_fields` (`fields: [...]`), `invalid_email`, `invalid_graduation_year`, `file_too_large`, `invalid_file_type`, `upload_failed`.
- `409 email_already_registered`.

## GET /users/get.php
- Query: `id` (positive int, required).
- `200` user object · `400 invalid_id` · `404 user_not_found`.

## GET /users/get_all.php
- Query: `query` (optional substring match on `email`, case-insensitive).
- `200` array of user objects (`[]` if none).

## POST /users/patch.php
- Body (same encoding as `post.php`). Required: `id`. At least one updatable field or a new `profile_picture` must be supplied. Empty/missing fields are left unchanged.
- Updatable: `name`, `email`, `password`, `graduation_year`, `field_of_study`, `current_role`, `company`, `location`, `bio`, `profile_picture` (replaces prior; old file deleted).
- `200 { "updated": N }`.
- `400`: `invalid_id`, `no_fields_to_update`, `invalid_email`, `invalid_graduation_year`, `file_too_large`, `invalid_file_type`, `upload_failed`.
- `404 user_not_found` · `409 email_already_registered`.

## POST /users/delete.php
- Body: `id` (positive int, required). Hard delete.
- Self-delete: if `id == $_SESSION['user_id']`, session is cleared and `PHPSESSID` is expired in the response.
- `200 { "deleted": N }` · `400 invalid_id` · `404 user_not_found`.

## Error envelope

All errors are JSON: `{ "error": "<code>", ...optional fields }`. Status codes: `400` validation, `401` auth, `404` missing row, `409` uniqueness conflict.

## Quick curl

```bash
# register
curl -X POST $BASE/users/post.php -F name=Jane -F email=j@x.io -F password=pw
# login (save cookie)
curl -c jar -X POST $BASE/users/login.php -d email=j@x.io -d password=pw
# read / list / search
curl -b jar "$BASE/users/get.php?id=1"
curl -b jar "$BASE/users/get_all.php?query=example.net"
# patch
curl -b jar -X POST $BASE/users/patch.php -F id=1 -F company=NewCo
# delete (self-delete also logs out)
curl -b jar -X POST $BASE/users/delete.php -d id=1
# logout
curl -b jar -X POST $BASE/users/logout.php
```

## Implementation notes
- Passwords hashed with SHA-256 (matches seed data; production should migrate to bcrypt via `password_hash` / `password_verify`).
- Uploads stored at `/uploads/{uuid}.{ext}`; `patch.php` deletes the prior file on replace.
- `email` substring filter in `get_all.php` follows the column's collation.
- Cookie flags: `HttpOnly`, `SameSite=Lax`, `Secure` over HTTPS.
