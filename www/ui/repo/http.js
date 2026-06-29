export const API_BASE = new URL('../../', import.meta.url).pathname.replace(/\/$/, '');

export class ApiError extends Error {
  constructor(status, body) {
    const code = (body && body.error) || 'http_error';
    super(`${code} (HTTP ${status})`);
    this.name = 'ApiError';
    this.status = status;
    this.body = body || {};
    this.code = code;
  }
}

async function readBody(res) {
  const text = await res.text();
  if (!text) return null;
  try { return JSON.parse(text); }
  catch { return { error: 'invalid_json', raw: text }; }
}

export async function request(path, init = {}) {
  const res = await fetch(`${API_BASE}${path}`, { credentials: 'include', ...init });
  const body = await readBody(res);
  if (!res.ok) throw new ApiError(res.status, body);
  return body;
}

export function toFormData(fields) {
  const fd = new FormData();
  for (const [key, value] of Object.entries(fields || {})) {
    if (value === null || value === undefined) continue;
    fd.append(key, value);
  }
  return fd;
}

export function buildQuery(params) {
  const usp = new URLSearchParams();
  for (const [key, value] of Object.entries(params || {})) {
    if (value === null || value === undefined || value === '') continue;
    usp.append(key, String(value));
  }
  const qs = usp.toString();
  return qs ? `?${qs}` : '';
}
