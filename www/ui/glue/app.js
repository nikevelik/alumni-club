import * as Users from '../repo/users_repository.js';
import * as Events from '../repo/event_repository.js';
import { rememberSession, forgetSession, rememberedUserId } from './session.js';
import { show, showError, renderUserCard, renderUsers, renderEvents } from './render.js';

// Build a plain object from a <form>. Empty strings are omitted so patch
// requests don't overwrite existing values with blanks.
function formToObject(form) {
  const fd = new FormData(form);
  const out = {};
  fd.forEach((value, key) => {
    if (value instanceof File) return; // files are pulled separately
    if (value === '') return;
    out[key] = value;
  });
  return out;
}

function fileFromForm(form, fieldName) {
  const input = form.elements[fieldName];
  if (!input || !input.files || input.files.length === 0) return null;
  const f = input.files[0];
  return f && f.size > 0 ? f : null;
}

// ---------- session status ----------

function renderSession() {
  const id = rememberedUserId();
  document.getElementById('session-status').textContent = id
    ? `logged in as user #${id}`
    : 'not logged in (cookie may still be valid — try any call)';
}

// ---------- Registration ----------

document.getElementById('register-form').addEventListener('submit', e => {
  e.preventDefault();
  const form = e.target;
  const out = document.getElementById('register-out');
  Users.createUser(formToObject(form), fileFromForm(form, 'profile_picture'))
    .then(res => { show(out, res); form.reset(); })
    .catch(err => showError(out, err));
});

// ---------- Login ----------

document.getElementById('login-form').addEventListener('submit', e => {
  e.preventDefault();
  const form = e.target;
  const fields = formToObject(form);
  const out = document.getElementById('login-out');
  Users.login({ email: fields.email, password: fields.password })
    .then(res => {
      show(out, res);
      if (res && res.id) { rememberSession(res.id); renderSession(); }
      form.reset();
    })
    .catch(err => showError(out, err));
});

// ---------- Logout ----------

document.getElementById('logout-btn').addEventListener('click', () => {
  const out = document.getElementById('logout-out');
  Users.logout()
    .then(res => { show(out, res); forgetSession(); renderSession(); })
    .catch(err => {
      showError(out, err);
      // 401 not_logged_in still means we're logged out — clear local state too.
      if (err && err.status === 401) { forgetSession(); renderSession(); }
    });
});

// ---------- Get one user ----------

document.getElementById('get-user-form').addEventListener('submit', e => {
  e.preventDefault();
  const id = parseInt(e.target.elements.id.value, 10);
  const out = document.getElementById('get-user-out');
  Users.getUser(id)
    .then(user => { out.innerHTML = renderUserCard(user); })
    .catch(err => { out.textContent = ''; showError(out, err); });
});

// ---------- Edit profile ----------

const editForm = document.getElementById('edit-form');
const rememberedId = rememberedUserId();
if (rememberedId) editForm.elements.id.value = rememberedId;

editForm.addEventListener('submit', e => {
  e.preventDefault();
  const all = formToObject(e.target);
  const id = parseInt(all.id, 10);
  delete all.id;
  const out = document.getElementById('edit-out');
  Users.updateUser(id, all, fileFromForm(e.target, 'profile_picture'))
    .then(res => show(out, res))
    .catch(err => showError(out, err));
});

document.getElementById('edit-delete-btn').addEventListener('click', () => {
  const id = parseInt(editForm.elements.id.value, 10);
  const out = document.getElementById('edit-out');
  if (!id) { out.textContent = 'Enter a user id first.'; return; }
  if (!confirm(`Delete user #${id}? This cannot be undone.`)) return;
  Users.deleteUser(id)
    .then(res => {
      show(out, res);
      // Self-delete clears the server session; reflect that locally.
      if (rememberedUserId() === id) { forgetSession(); renderSession(); }
    })
    .catch(err => showError(out, err));
});

// ---------- Users ----------

document.getElementById('search-users-form').addEventListener('submit', e => {
  e.preventDefault();
  const out = document.getElementById('search-users-out');
  Users.getAllUsers(e.target.elements.query.value)
    .then(users => renderUsers(out, users))
    .catch(err => { out.textContent = ''; showError(out, err); });
});

// ---------- Create event ----------

document.getElementById('create-event-form').addEventListener('submit', e => {
  e.preventDefault();
  const form = e.target;
  const out = document.getElementById('create-event-out');
  Events.createEvent(formToObject(form))
    .then(res => { show(out, res); form.reset(); })
    .catch(err => showError(out, err));
});

// ---------- Events ----------

document.getElementById('search-events-form').addEventListener('submit', e => {
  e.preventDefault();
  const out = document.getElementById('search-events-out');
  Events.getAllEvents(e.target.elements.query.value)
    .then(events => renderEvents(out, events))
    .catch(err => { out.textContent = ''; showError(out, err); });
});

// ---------- bootstrap ----------
renderSession();
