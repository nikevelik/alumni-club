import { API_BASE } from '../repo/users_repository.js';

function escapeHtml(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function show(el, value) {
  if (typeof value === 'string') el.textContent = value;
  else el.textContent = JSON.stringify(value, null, 2);
}

export function showError(el, err) {
  if (err && err.name === 'ApiError') {
    show(el, 'HTTP ' + err.status + '\n' + JSON.stringify(err.body, null, 2));
  } else {
    show(el, 'Network error: ' + (err && err.message ? err.message : err));
  }
}

export function renderUserCard(user) {
  const img = user.profile_picture
    ? `<img src="${escapeHtml(API_BASE + user.profile_picture)}" alt="" width="64" height="64">`
    : '';
  return `<article>
    <h3>#${user.id} — ${escapeHtml(user.name)}</h3>
    ${img}
    <ul>
      <li>Email: ${escapeHtml(user.email)}</li>
      <li>Graduation year: ${escapeHtml(user.graduation_year)}</li>
      <li>Field of study: ${escapeHtml(user.field_of_study)}</li>
      <li>Current role: ${escapeHtml(user.current_role)}</li>
      <li>Company: ${escapeHtml(user.company)}</li>
      <li>Location: ${escapeHtml(user.location)}</li>
      <li>Bio: ${escapeHtml(user.bio)}</li>
    </ul>
  </article>`;
}

export function renderEventCard(ev) {
  return `<article>
    <h3>#${ev.id} — ${escapeHtml(ev.name)}</h3>
    <ul>
      <li>Date: ${escapeHtml(ev.date)}</li>
      <li>Details: ${escapeHtml(ev.details)}</li>
      <li>Creator: user #${escapeHtml(ev.creator)}</li>
    </ul>
  </article>`;
}

export function renderUsers(container, users) {
  if (!Array.isArray(users) || users.length === 0) {
    container.innerHTML = '<p>No users.</p>';
    return;
  }
  container.innerHTML = users.map(renderUserCard).join('<hr>');
}

export function renderEvents(container, events) {
  if (!Array.isArray(events) || events.length === 0) {
    container.innerHTML = '<p>No events.</p>';
    return;
  }
  container.innerHTML = events.map(renderEventCard).join('<hr>');
}
