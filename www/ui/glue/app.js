import * as Users from '../repo/users_repository.js';
import * as Events from '../repo/event_repository.js';
import { rememberSession, forgetSession, rememberedUserId } from './session.js';
import {
  renderUsers, renderEvents, renderUserDetail, renderProfileSummary,
} from './render.js';
import { toastOk, toastError } from './toast.js';

// ---------- helpers ----------

// FormData → plain object. Empty strings are dropped so patch requests don't
// overwrite existing values; files are skipped (caller pulls them separately).
function formToObject(form) {
  const fd = new FormData(form);
  const out = {};
  fd.forEach((value, key) => {
    if (value instanceof File) return;
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

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

// Toggle visibility via a CSS utility class instead of the `hidden` attribute.
// The attribute relies on the UA's `[hidden] { display: none }` rule, which
// loses specificity ties to any class rule that sets `display` (e.g. flex/grid
// layouts), causing toggles to be silently ignored. `.is-hidden` uses
// `!important` and wins unconditionally — see styles.css.
function setHidden(el, hide) {
  if (!el) return;
  el.classList.toggle('is-hidden', !!hide);
}

// ---------- auth UI state ----------

// Toggles every element gated on session presence. Driven by rememberedUserId()
// rather than a separate flag so tab refresh after login stays consistent.
function applyAuthState() {
  const userId = rememberedUserId();
  const signedIn = !!userId;

  // Pill + sign-out button in the header.
  const pill = $('#session-pill');
  if (signedIn) {
    pill.textContent = `Signed in · user #${userId}`;
    pill.className = 'session-pill session-pill--in';
  } else {
    pill.textContent = 'Signed out';
    pill.className = 'session-pill session-pill--out';
  }
  setHidden($('#logout-btn'), !signedIn);

  // Nav items: profile only when signed in, "Sign in" only when out.
  $$('[data-requires-auth]').forEach((el) => setHidden(el, !signedIn));
  $$('[data-hidden-when-auth]').forEach((el) => setHidden(el, signedIn));

  // If currently on a route that just became forbidden, fall back to directory.
  const route = document.querySelector('.app').dataset.route;
  if (!signedIn && (route === 'profile')) routeTo('directory');
}

// ---------- routing (in-page tabs, no URL changes) ----------

function routeTo(name) {
  document.querySelector('.app').dataset.route = name;
  $$('.nav-item').forEach((btn) => {
    btn.classList.toggle('is-active', btn.dataset.route === name);
  });
  $$('.view').forEach((v) => setHidden(v, v.dataset.view !== name));

  if (name === 'directory') loadUsers('');
  if (name === 'events') loadEvents('');
  if (name === 'profile') loadProfile();
}

$$('.nav-item').forEach((btn) => {
  btn.addEventListener('click', () => routeTo(btn.dataset.route));
});

// ---------- data loaders ----------

function loadUsers(query) {
  const out = $('#users-out');
  out.innerHTML = `<div class="empty-state">Loading…</div>`;
  Users.getAllUsers(query)
    .then((users) => renderUsers(out, users))
    .catch((err) => {
      out.innerHTML = `<div class="empty-state">Couldn't load users.</div>`;
      toastError('Search failed', err);
    });
}

function loadEvents(query) {
  const out = $('#events-out');
  out.innerHTML = `<div class="empty-state">Loading…</div>`;
  Events.getAllEvents(query)
    .then((events) => renderEvents(out, events, rememberedUserId()))
    .catch((err) => {
      out.innerHTML = `<div class="empty-state">Couldn't load events.</div>`;
      toastError('Search failed', err);
    });
}

// Profile view: fetch own record, fill the summary card and pre-populate the
// edit form's hidden id. Profile-edit only edits the *current* user — the API
// allows arbitrary ids but the UI does not expose that.
function loadProfile() {
  const id = rememberedUserId();
  if (!id) return;
  Users.getUser(id)
    .then((user) => {
      renderProfileSummary($('#profile-summary'), user);
      const form = $('#edit-form');
      form.elements.name.value = user.name || '';
      form.elements.email.value = user.email || '';
      form.elements.graduation_year.value = user.graduation_year || '';
      form.elements.field_of_study.value = user.field_of_study || '';
      form.elements.current_role.value = user.current_role || '';
      form.elements.company.value = user.company || '';
      form.elements.location.value = user.location || '';
      form.elements.bio.value = user.bio || '';
    })
    .catch((err) => toastError('Profile load failed', err));
}

// ---------- user detail modal ----------

const userModal = $('#user-modal');

$('#users-out').addEventListener('click', (e) => {
  const card = e.target.closest('[data-user-id]');
  if (!card) return;
  const id = parseInt(card.dataset.userId, 10);
  Users.getUser(id)
    .then((user) => {
      $('#user-modal-body').innerHTML = renderUserDetail(user);
      userModal.showModal();
    })
    .catch((err) => toastError('Could not load user', err));
});

// ---------- forms ----------

// Register
$('#register-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const form = e.target;
  Users.createUser(formToObject(form), fileFromForm(form, 'profile_picture'))
    .then((res) => {
      toastOk('Account created', `user #${res.id}`);
      form.reset();
      // Auto-login is not provided by the API; just send them to the sign-in card.
      // (No nav change — the auth view already has both side by side.)
    })
    .catch((err) => toastError('Registration failed', err));
});

// Login
$('#login-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const form = e.target;
  const fields = formToObject(form);
  Users.login({ email: fields.email, password: fields.password })
    .then((res) => {
      if (res && res.id) {
        rememberSession(res.id);
        applyAuthState();
        form.reset();
        toastOk('Welcome back', `Signed in as user #${res.id}`);
        routeTo('directory');
      }
    })
    .catch((err) => toastError('Sign-in failed', err));
});

// Logout (header button)
$('#logout-btn').addEventListener('click', () => {
  Users.logout()
    .then(() => {
      forgetSession();
      applyAuthState();
      toastOk('Signed out');
      routeTo('directory');
    })
    .catch((err) => {
      // 401 not_logged_in still means we're effectively signed out — clean up.
      if (err && err.status === 401) {
        forgetSession();
        applyAuthState();
        routeTo('directory');
      } else {
        toastError('Sign-out failed', err);
      }
    });
});

// Directory search
$('#search-users-form').addEventListener('submit', (e) => {
  e.preventDefault();
  loadUsers(e.target.elements.query.value);
});

// Events search
$('#search-events-form').addEventListener('submit', (e) => {
  e.preventDefault();
  loadEvents(e.target.elements.query.value);
});

// Create event
$('#create-event-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const form = e.target;
  Events.createEvent(formToObject(form))
    .then((res) => {
      toastOk('Event published', `#${res.id}`);
      form.reset();
      form.closest('details')?.removeAttribute('open');
      loadEvents('');
    })
    .catch((err) => toastError('Could not publish event', err));
});

// Event delete (event-delegated on the cards container)
$('#events-out').addEventListener('click', (e) => {
  const btn = e.target.closest('.delete-event-btn');
  if (!btn) return;
  e.stopPropagation();
  const card = btn.closest('[data-event-id]');
  const id = parseInt(card.dataset.eventId, 10);
  if (!confirm(`Delete event #${id}? This cannot be undone.`)) return;
  Events.deleteEvent(id)
    .then(() => { toastOk('Event deleted', `#${id}`); loadEvents(''); })
    .catch((err) => toastError('Delete failed', err));
});

// Profile edit
$('#edit-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const id = rememberedUserId();
  if (!id) { toastError('Not signed in', 'Sign in to edit your profile.'); return; }
  const fields = formToObject(e.target);
  Users.updateUser(id, fields, fileFromForm(e.target, 'profile_picture'))
    .then(() => { toastOk('Profile updated'); loadProfile(); })
    .catch((err) => toastError('Update failed', err));
});

// Delete own account
$('#delete-self-btn').addEventListener('click', () => {
  const id = rememberedUserId();
  if (!id) return;
  if (!confirm(`Delete your account (user #${id})? This cannot be undone.`)) return;
  Users.deleteUser(id)
    .then(() => {
      // Self-delete clears the server session; mirror locally.
      forgetSession();
      applyAuthState();
      toastOk('Account deleted');
      routeTo('directory');
    })
    .catch((err) => toastError('Account deletion failed', err));
});

// ---------- bootstrap ----------

applyAuthState();
routeTo(rememberedUserId() ? 'directory' : 'auth');
