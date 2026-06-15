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
  if (!res.ok) throw new ApiError(res.status, body);
  return body;
}

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

export { API_BASE, ApiError };

export function login({ email, password }) {
  return request('/users/login.php', {
    method: 'POST',
    body: toFormData({ email, password }),
  });
}

export function logout() {
  return request('/users/logout.php', { method: 'POST' });
}

export function getUser(id) {
  return request(`/users/get.php${buildQuery({ id })}`);
}

export function getAllUsers(query) {
  return request(`/users/get_all.php${buildQuery({ query })}`);
}

export function createUser(user, profilePicture) {
  const fields = { ...user };
  if (profilePicture) fields.profile_picture = profilePicture;
  return request('/users/post.php', {
    method: 'POST',
    body: toFormData(fields),
  });
}

export function updateUser(id, patch, profilePicture) {
  const fields = { id, ...patch };
  if (profilePicture) fields.profile_picture = profilePicture;
  return request('/users/patch.php', {
    method: 'POST',
    body: toFormData(fields),
  });
}

export function deleteUser(id) {
  return request('/users/delete.php', {
    method: 'POST',
    body: toFormData({ id }),
  });
}
