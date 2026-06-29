
const HOST_ID = 'toast-host';
const DEFAULT_TTL = 3500;

const ERROR_MESSAGES = {
  missing_required_fields:  'Please fill in all required fields.',
  invalid_email:            'The email address is not valid.',
  email_already_registered: 'That email is already registered.',
  invalid_graduation_year:  'Please enter a valid graduation year.',
  invalid_id:               'Invalid ID.',
  user_not_found:           'User not found.',
  event_not_found:          'Event not found.',
  creator_not_found:        'The event creator could not be found.',
  no_fields_to_update:      'No changes were made.',
  field_too_long:           'One or more fields exceed the maximum allowed length.',
  invalid_credentials:      'Incorrect email or password.',
  not_logged_in:            'You must be signed in to do that.',
  file_too_large:           'The file is too large to upload.',
  invalid_file_type:        'Only image files (JPEG, PNG, GIF, WebP) are allowed.',
  upload_failed:            'The file upload failed. Please try again.',
  no_file_uploaded:         'No file was selected.',
  uploads_dir_not_writable: 'The server cannot accept uploads right now.',
  invalid_json:             'The server returned an unexpected response.',
  http_error:               'An unexpected error occurred.',
};

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

export function toastError(title, err) {
  let detail = '';
  if (err && err.name === 'ApiError') {
    detail = ERROR_MESSAGES[err.code] || ERROR_MESSAGES.http_error;
    if (err.body && err.body.fields) {
      detail += ` (${err.body.fields.join(', ')})`;
    }
  } else if (err && err.message) {
    detail = err.message;
  } else if (typeof err === 'string') {
    detail = err;
  }
  push({ kind: 'err', title, detail });
}
