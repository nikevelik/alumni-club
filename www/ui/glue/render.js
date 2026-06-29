export function escapeHtml(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function initials(name) {
  if (!name) return '?';
  const parts = String(name).trim().split(/\s+/);
  const a = parts[0]?.[0] ?? '';
  const b = parts.length > 1 ? parts[parts.length - 1][0] : '';
  return (a + b).toUpperCase() || '?';
}

function avatar(user) {
  if (user.profile_picture) {
    return `<div class="card-avatar"><img src="${escapeHtml(user.profile_picture)}" alt=""></div>`;
  }
  return `<div class="card-avatar">${escapeHtml(initials(user.name))}</div>`;
}

export function renderUserCard(user) {
  const role = [user.current_role, user.company].filter(Boolean).map(escapeHtml).join(' · ');
  return `
    <article class="card" data-user-id="${user.id}">
      <div class="card-head">
        ${avatar(user)}
        <div>
          <div class="card-title">${escapeHtml(user.name)}</div>
          <div class="card-subtitle">${role || '&nbsp;'}</div>
        </div>
      </div>
      <div class="card-meta">
        <div><strong>Email:</strong> ${escapeHtml(user.email)}</div>
        ${user.graduation_year ? `<div><strong>Class of:</strong> ${escapeHtml(user.graduation_year)}</div>` : ''}
        ${user.location ? `<div><strong>Location:</strong> ${escapeHtml(user.location)}</div>` : ''}
      </div>
    </article>`;
}

export function renderUsers(container, users) {
  if (!Array.isArray(users) || users.length === 0) {
    container.innerHTML = `<div class="empty-state">No alumni match that search.</div>`;
    return;
  }
  container.innerHTML = users.map(renderUserCard).join('');
}

export function renderUserDetail(user) {
  const rows = [
    ['Email', user.email],
    ['Graduation year', user.graduation_year],
    ['Field of study', user.field_of_study],
    ['Current role', user.current_role],
    ['Company', user.company],
    ['Location', user.location],
    ['Bio', user.bio],
  ].filter(([, v]) => v !== null && v !== undefined && v !== '');

  const lines = rows.map(([k, v]) => `<div><strong>${k}:</strong> ${escapeHtml(v)}</div>`).join('');
  return `
    <div class="card-head" style="margin-bottom: 1rem;">
      ${avatar(user)}
      <div>
        <div class="card-title">${escapeHtml(user.name)}</div>
        <div class="card-subtitle">User #${escapeHtml(user.id)}</div>
      </div>
    </div>
    <div class="card-meta">${lines || '<em>No additional details.</em>'}</div>`;
}

export function renderEventCard(ev, currentUserId) {
  const ownActions = currentUserId && Number(ev.creator) === Number(currentUserId)
    ? `<div class="card-actions"><button type="button" class="btn btn-danger delete-event-btn">Delete</button></div>`
    : '';
  return `
    <article class="card" data-event-id="${ev.id}">
      <div class="card-title">${escapeHtml(ev.name)}</div>
      <div class="card-subtitle">${escapeHtml(ev.date)}</div>
      <div class="card-meta">
        ${ev.details ? `<div>${escapeHtml(ev.details)}</div>` : ''}
        <div><strong>Organizer:</strong> user #${escapeHtml(ev.creator)}</div>
      </div>
      ${ownActions}
    </article>`;
}

export function renderEvents(container, events, currentUserId) {
  if (!Array.isArray(events) || events.length === 0) {
    container.innerHTML = `<div class="empty-state">No events scheduled.</div>`;
    return;
  }
  container.innerHTML = events.map(e => renderEventCard(e, currentUserId)).join('');
}

export function renderProfileSummary(container, user) {
  if (!user) { container.innerHTML = ''; return; }
  container.innerHTML = `
    ${avatar(user)}
    <div>
      <div class="name">${escapeHtml(user.name)}</div>
      <div class="meta">${escapeHtml(user.email)} · user #${escapeHtml(user.id)}</div>
    </div>`;
}
