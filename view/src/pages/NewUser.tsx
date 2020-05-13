import React from 'react';
import styled from 'styled-components';
import User from '../models/user';
import UserSettingsForm from '../components/UserSettingsForm';
import { getEventTypes, getEmailSettings, createNewUser } from '../backend_interface/api_interface';

function NewUser(): JSX.Element {
    const user = InitUser();

    return (
        <UserSettingsForm user={user} submitRequest={createNewUser} />
    )
}

function InitUser(): User {
    let user = new User();
    user.eventTypes = getEventTypes();
    user.emailSettings = getEmailSettings();

    return user;
}

export default NewUser;