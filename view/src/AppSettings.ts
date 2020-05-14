const API_DOMAIN = 'http://localhost:5000'
export const PROCORE_LOGIN_URL = `${API_DOMAIN}/login`;
export const GCAL_LOGIN_URL = `${API_DOMAIN}/gcal_login`;
export const API_USER = (id: string) => `/api/users/${id}`
export const API_NEW_USER = '/api/users/new';