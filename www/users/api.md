# Users API

## GET /users/get.php

Returns a single user by ID.

**Query Parameters**

| Parameter | Type    | Required | Description     |
|-----------|---------|----------|-----------------|
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

`200 OK` — empty array if user not found or `id` is invalid:

```json
[]
```
