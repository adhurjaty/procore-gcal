const API_PREFIX = process.env.NODE_ENV === 'development' 
    ? 'http://localhost:5000'
    : '/api'
export const PROCORE_LOGIN_URL = `${API_PREFIX}/login`;
export const GCAL_USER_LOGIN_URL = (token: string) => 
    `${API_PREFIX}/gcal_login?auth_token=${token}`;
export const GCAL_COLLABORATOR_LOGIN_URL = (id: string) => 
    `${API_PREFIX}/gcal_login?collaborator_id=${id}`;
export const API_USER = (id: string) => `${API_PREFIX}/users/${id}`
export const API_NEW_COLLABORATOR = (id: string) => `${API_PREFIX}/collaborators/${id}`
export const API_NEW_USER = `${API_PREFIX}/users/new`;