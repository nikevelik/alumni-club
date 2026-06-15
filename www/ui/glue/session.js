const SESSION_KEY = 'alumni_session_user_id';

// The PHPSESSID cookie is the source of truth for "am I logged in?",
// but JS can't read HttpOnly cookies, so we mirror the user's id in
// localStorage on login/logout. This is purely for the UI status line
// and to prefill the "edit profile" form — every actual API call still
// relies on the cookie that the browser sends automatically.

export function rememberSession(userId) {
  try { localStorage.setItem(SESSION_KEY, String(userId)); } catch (_) {}
}

export function forgetSession() {
  try { localStorage.removeItem(SESSION_KEY); } catch (_) {}
}

export function rememberedUserId() {
  try {
    const v = localStorage.getItem(SESSION_KEY);
    return v ? parseInt(v, 10) : null;
  } catch (_) { return null; }
}
