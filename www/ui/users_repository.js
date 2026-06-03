// Users API client.
//
// One function per endpoint of www/users/*.php, calling the remote host
// directly. Each function returns a Promise that resolves to the parsed
// JSON body on a 2xx response, or rejects with an `ApiError` on any non-2xx
// (the error body from the server is exposed as `err.body`, the status as
// `err.status`).
//
// Cookies (the PHPSESSID session) are sent on every request via
// `credentials: 'include'`; the browser must allow third-party cookies for
// the API origin, and the server must reply with the appropriate CORS
// headers (Access-Control-Allow-Origin: <page origin>,
// Access-Control-Allow-Credentials: true) for cross-origin use.

(function () {

const API_BASE = 'http://35.208.59.90';

class ApiError extends Error {
  constructor(status, body) {
    const code = (body && body.error) || 'http_error';
    super(`${code} (HTTP ${status})`);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

// ---------- internal helpers ----------

// Parse the response body as JSON when possible; fall back to text so an
// HTML error page from the front proxy doesn't blow up with a parse error.
async function readBody(res) {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return { error: 'invalid_json', raw: text };
  }
}

async function request(path, init = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    ...init,
  });
  const body = await readBody(res);
  if (!res.ok) {
    throw new ApiError(res.status, body);
  }
  return body;
}

// Build a FormData from a plain object. `null`/`undefined` values are
// skipped so callers can pass partial patches without scrubbing them
// first. File values (Blob/File) are forwarded as-is.
function toFormData(fields) {
  const fd = new FormData();
  for (const [key, value] of Object.entries(fields || {})) {
    if (value === null || value === undefined) continue;
    fd.append(key, value);
  }
  return fd;
}

function buildQuery(params) {
  const usp = new URLSearchParams();
  for (const [key, value] of Object.entries(params || {})) {
    if (value === null || value === undefined || value === '') continue;
    usp.append(key, String(value));
  }
  const qs = usp.toString();
  return qs ? `?${qs}` : '';
}

// ---------- endpoints ----------

// POST /users/login.php — authenticate and start a session.
// Resolves to { id, logged_in: true } on success.
function login({ email, password }) {
  return request('/users/login.php', {
    method: 'POST',
    body: toFormData({ email, password }),
  });
}

// POST /users/logout.php — clear the current session.
// Resolves to { logged_out: <id> }; 401 not_logged_in if no session.
function logout() {
  return request('/users/logout.php', { method: 'POST' });
}

// GET /users/get.php?id=<id> — fetch a single user.
// Resolves to the user object; 404 user_not_found / 400 invalid_id on errors.
function getUser(id) {
  return request(`/users/get.php${buildQuery({ id })}`);
}

// GET /users/get_all.php[?query=<substring>] — list users, optionally
// filtered by an email substring (case-insensitive). Resolves to an array.
function getAllUsers(query) {
  return request(`/users/get_all.php${buildQuery({ query })}`);
}

// POST /users/post.php — register a new user.
// `user` is a plain object whose keys match the api.md body parameters
// (name, email, password, graduation_year, field_of_study, current_role,
// company, location, bio). `profilePicture`, if provided, must be a File
// or Blob. Resolves to { id }.
function createUser(user, profilePicture) {
  const fields = { ...user };
  if (profilePicture) fields.profile_picture = profilePicture;
  return request('/users/post.php', {
    method: 'POST',
    body: toFormData(fields),
  });
}

// POST /users/patch.php — partial update. `id` is required; pass any
// subset of patchable fields in `patch`. `profilePicture`, if provided,
// must be a File or Blob and replaces the current picture. Resolves to
// { updated: <id> }.
function updateUser(id, patch, profilePicture) {
  const fields = { id, ...patch };
  if (profilePicture) fields.profile_picture = profilePicture;
  return request('/users/patch.php', {
    method: 'POST',
    body: toFormData(fields),
  });
}

// POST /users/delete.php — hard-delete a user.
// Self-delete clears the caller's session as a side effect. Resolves to
// { deleted: <id> }.
function deleteUser(id) {
  return request('/users/delete.php', {
    method: 'POST',
    body: toFormData({ id }),
  });
}

// Exposed as a global namespace so plain <script src=...> tags can use it
// without a module loader. window.UsersRepo.login(...), etc.
window.UsersRepo = {
  ApiError,
  API_BASE,
  login,
  logout,
  getUser,
  getAllUsers,
  createUser,
  updateUser,
  deleteUser,
};

})();
