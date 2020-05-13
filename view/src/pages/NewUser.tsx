import React from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom'
import User from '../models/user';
import UserSettingsForm from '../components/UserSettingsForm';
import { NEW_USER_ROUTE } from '../Routes';
import { API_NEW_USER } from '../AppSettings';

function NewUser(): JSX.Element {
    const user = new User();

    let requestFn = (user: User) => {
        return new Request(API_NEW_USER, {
            method: 'POST',
            body: JSON.stringify(user.toJson())
        });
    }

    return (
        <UserSettingsForm user={user} submitRequest={requestFn} />
    )
}

function CreateNewUser(): User {
    let user = new User();
    
}

export default NewUser;