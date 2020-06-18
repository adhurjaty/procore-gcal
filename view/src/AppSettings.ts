// const API_DOMAIN = 'http://localhost:5000'
export const PROCORE_LOGIN_URL = '/api/login';
export const GCAL_USER_LOGIN_URL = (token: string) => 
    `/api/gcal_login?auth_token=${token}`;
export const GCAL_COLLABORATOR_LOGIN_URL = (id: string) => 
    `/api/gcal_login?collaborator_id=${id}`;
export const API_USER = (id: string) => `/api/users/${id}`
export const API_NEW_COLLABORATOR = (id: string) => `/api/collaborators/${id}`
export const API_NEW_USER = '/api/users/new';