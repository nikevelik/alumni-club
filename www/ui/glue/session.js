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
