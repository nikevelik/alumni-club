import { request, buildQuery, toFormData } from './http.js';

export function login({ email, password }) {
  return request('/users/login.php', { method: 'POST', body: toFormData({ email, password }) });
}

export function logout() {
  return request('/users/logout.php', { method: 'POST' });
}

export function getUser(id) {
  return request(`/users/get.php${buildQuery({ id })}`);
}

export function getAllUsers(query) {
  return request(`/users/get_all.php${buildQuery({ query })}`);
}

export function createUser(user, profilePicture) {
  const fields = { ...user };
  if (profilePicture) fields.profile_picture = profilePicture;
  return request('/users/post.php', { method: 'POST', body: toFormData(fields) });
}

export function updateUser(id, patch, profilePicture) {
  const fields = { id, ...patch };
  if (profilePicture) fields.profile_picture = profilePicture;
  return request('/users/patch.php', { method: 'POST', body: toFormData(fields) });
}

export function deleteUser(id) {
  return request('/users/delete.php', { method: 'POST', body: toFormData({ id }) });
}
