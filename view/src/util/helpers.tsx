import Cookies from 'js-cookie'

export function LogOut() {
    Cookies.remove('auth_token');
}

export function IsLoggedIn(): boolean {
    return !!Cookies.get('auth_token');
}