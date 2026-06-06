The UI is a single page at `www/index.html` with no framework or build step. Sections are native `<details>`/`<summary>` accordion panels.

The only script tag is `<script type="module" src="ui/glue/app.js">`. All other JS files are loaded via ES module imports — no globals, no load-order dependencies.

---

The JS is split across five files:

`ui/repo/users_repository.js` — fetch wrapper for the users API. Exports one function per endpoint: `login`, `logout`, `getUser`, `getAllUsers`, `createUser`, `updateUser`, `deleteUser`. Also exports `API_BASE` and `ApiError`.

`ui/repo/event_repository.js` — same pattern for the events API. Exports `getEvent`, `getAllEvents`, `createEvent`, `deleteEvent`.

`ui/glue/session.js` — thin localStorage wrapper. Exports `rememberSession`, `forgetSession`, `rememberedUserId`. The PHPSESSID cookie is the real auth token; this just mirrors the logged-in user's ID so the UI can display it and prefill the edit form.

`ui/glue/render.js` — pure rendering helpers. Exports `show`, `showError`, `renderUserCard`, `renderEventCard`, `renderUsers`, `renderEvents`.

`ui/glue/app.js` — entry point. Imports from all four files above, wires up form and button event listeners, and calls `renderSession()` on load.

---

Panels and what they do:

- Registration — create a user (`POST /users/post.php`)
- Login — start a session (`POST /users/login.php`)
- Logout — end the session (`POST /users/logout.php`)
- User data — fetch a single user by ID (`GET /users/get.php?id=`)
- Edit profile — patch a user or delete them (`POST /users/patch.php`, `POST /users/delete.php`)
- All users — list all users (`GET /users/get_all.php`)
- Search users — filter users by email substring (`GET /users/get_all.php?query=`)
- Create event — create an event (`POST /events/post.php`)
- All events — list all events (`GET /events/get_all.php`)
- Search events — filter events by name substring (`GET /events/get_all.php?query=`)

Empty form fields are stripped before sending so patch requests don't overwrite existing values with blanks. Errors display as `HTTP <status>` + JSON body in the same output area as success responses.
