// Mirror of the server-side session: PHP holds the source of truth in an
// HttpOnly cookie (PHPSESSID) so JS can't read it. We mirror the user's id in
// localStorage on login/logout. This is purely for UI ("am I logged in?"),
// never for authorization — every protected call relies on the cookie.

const KEY = 'alumni_session_user_id';

export function rememberSession(userId) {
  try { localStorage.setItem(KEY, String(userId)); } catch (_) {}
}

export function forgetSession() {
  try { localStorage.removeItem(KEY); } catch (_) {}
}

export function rememberedUserId() {
  try {
    const v = localStorage.getItem(KEY);
    return v ? parseInt(v, 10) : null;
  } catch (_) { return null; }
}
