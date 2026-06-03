// Events API client.
//
// One function per endpoint of www/events/*.php, calling the remote host
// directly. Same conventions as users_repository.js: returns the parsed
// JSON body on a 2xx response, or throws an `ApiError` with `.status`
// and `.body` on any non-2xx.
//
// Every events endpoint is auth-gated, so the caller must already have a
// session (see users_repository.js#login). Cookies flow via
// `credentials: 'include'`.

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
// skipped so callers can pass partial objects without scrubbing them
// first.
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

// GET /events/get.php?id=<id> — fetch a single event.
// Resolves to the event object; 404 event_not_found / 400 invalid_id on errors.
function getEvent(id) {
  return request(`/events/get.php${buildQuery({ id })}`);
}

// GET /events/get_all.php[?query=<substring>] — list events, optionally
// filtered by a name substring (case-insensitive). Resolves to an array.
function getAllEvents(query) {
  return request(`/events/get_all.php${buildQuery({ query })}`);
}

// POST /events/post.php — create a new event.
// `event` keys mirror api.md: { date: 'YYYY-MM-DD', name, details?, creator }.
// Resolves to { id }.
function createEvent(event) {
  return request('/events/post.php', {
    method: 'POST',
    body: toFormData(event),
  });
}

// POST /events/delete.php — hard-delete an event. Resolves to { deleted: <id> }.
function deleteEvent(id) {
  return request('/events/delete.php', {
    method: 'POST',
    body: toFormData({ id }),
  });
}

// Exposed as a global namespace so plain <script src=...> tags can use it
// without a module loader. window.EventsRepo.getAllEvents(...), etc.
window.EventsRepo = {
  ApiError,
  API_BASE,
  getEvent,
  getAllEvents,
  createEvent,
  deleteEvent,
};

})();
