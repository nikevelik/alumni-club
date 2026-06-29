// Toast notifications. Append a node into #toast-host, auto-remove after a
// timeout. No external dependencies; styling lives in styles.css.

const HOST_ID = 'toast-host';
const DEFAULT_TTL = 3500;

function host() {
  return document.getElementById(HOST_ID);
}

function escape(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function push({ kind, title, detail }) {
  const h = host();
  if (!h) return;
  const node = document.createElement('div');
  node.className = `toast toast--${kind}`;
  node.innerHTML = `<strong>${escape(title)}</strong>${detail ? `<span>${escape(detail)}</span>` : ''}`;
  h.appendChild(node);
  setTimeout(() => {
    node.style.transition = 'opacity 0.2s';
    node.style.opacity = '0';
    setTimeout(() => node.remove(), 220);
  }, DEFAULT_TTL);
}

export function toastOk(title, detail) { push({ kind: 'ok', title, detail }); }
export function toastInfo(title, detail) { push({ kind: 'info', title, detail }); }

// Pretty-print ApiError-shaped failures. Falls back to raw text otherwise.
export function toastError(title, err) {
  let detail = '';
  if (err && err.name === 'ApiError') {
    detail = `${err.code} (HTTP ${err.status})`;
    if (err.body && err.body.fields) {
      detail += ` — fields: ${err.body.fields.join(', ')}`;
    }
  } else if (err && err.message) {
    detail = err.message;
  } else if (typeof err === 'string') {
    detail = err;
  }
  push({ kind: 'err', title, detail });
}
