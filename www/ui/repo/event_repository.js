import { request, buildQuery, toFormData } from './http.js';

export function getEvent(id) {
  return request(`/events/get.php${buildQuery({ id })}`);
}

export function getAllEvents(query) {
  return request(`/events/get_all.php${buildQuery({ query })}`);
}

// `creator` is bound server-side from the session; never sent from the client.
export function createEvent(event) {
  return request('/events/post.php', { method: 'POST', body: toFormData(event) });
}

export function deleteEvent(id) {
  return request('/events/delete.php', { method: 'POST', body: toFormData({ id }) });
}
