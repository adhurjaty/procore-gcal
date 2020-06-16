import React from 'react'
import Cookies from 'js-cookie'
import Login from './Login';
import { Redirect } from 'react-router-dom';
import { LOGIN_ROUTE, USER_SETTINGS_ROUTE } from '../Routes';

export default function NotFound(): JSX.Element {
    const hasCookie = !!Cookies.get('auth_token');
    let location = LOGIN_ROUTE;
    if(hasCookie) {
        location = USER_SETTINGS_ROUTE;
    }

    return (
        <Redirect to={location} />
    )
}