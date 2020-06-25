import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom'
import { getUserSettings, updateUser, deleteUser } from '../backend_interface/api_interface';
import UserSettingsForm from '../components/UserSettingsForm';
import User from '../models/user';
import { USER_SETTINGS_ROUTE } from '../Routes';
import Cookies from 'js-cookie'

const DeleteUserButton = styled.button`
    background-color: red
`

function EditUser(): JSX.Element {
    let { userId } = useParams();
    const initState = {
        user: getUserFromLocalStorage(),
        isLoading: true
    };
    const [state, setState] = useState(initState)

    useEffect(() => {
        getUserSettings(userId).then((user) => {
            user = preventLocalOverwrite(state.user, user);
            localStoreUser(user);
            setState({
                isLoading: false,
                user: user
            });
            const url = USER_SETTINGS_ROUTE.replace(':userId', user.id);
            if(userId != user.id) {
                window.history.pushState('user page', 'user page', url);
            }
        })
        .catch((error) => {
            Cookies.remove('auth_token');
            window.location.href = '/';
        });
    }, [])

    return (
        <Display state={state} />
    )
}

function getUserFromLocalStorage(): User {
    let user = new User();
    user.fullName = localStorage.getItem('user.fullName') || '';
    user.calendars = JSON.parse(localStorage.getItem('user.calendars') || 'null');
    user.projects = JSON.parse(localStorage.getItem('user.projects') || 'null');
    user.emailSettings = JSON.parse(localStorage.getItem('user.emailSettings') || 'null');
    user.eventTypes = JSON.parse(localStorage.getItem('user.eventTypes') || 'null');
    user.email = localStorage.getItem('user.email') || '';
    
    const selectedCal = localStorage.getItem('user.selectedCalendar');
    if(selectedCal) {
        user.selectedCalendar = user.calendars.find(c => c.id == selectedCal);
    }

    const projectId = localStorage.getItem('user.projectId');
    if(projectId) {
        user.projectId = parseInt(projectId);
    }

    return user;
}

function preventLocalOverwrite(localUser: User, apiUser: User): User {
    apiUser.fullName = localUser.fullName || apiUser.fullName;
    apiUser.selectedCalendar = apiUser.calendars.find(c => 
        c.id === localUser.selectedCalendar?.id) || apiUser.selectedCalendar;
    apiUser.projectId = (apiUser.projects.find(p => p.id === localUser.projectId)?.id || 
        apiUser.projectId) as number | null
    apiUser.emailSettings = localUser.emailSettings || apiUser.emailSettings;
    apiUser.eventTypes = localUser.eventTypes || apiUser.eventTypes;

    return apiUser;
}

function localStoreUser(user: User) {
    localStorage.setItem('user.email', user.email);
    localStorage.setItem('user.calendars', JSON.stringify(user.calendars));
    localStorage.setItem('user.projects', JSON.stringify(user.projects));
    localStorage.setItem('user.eventTypes', JSON.stringify(user.eventTypes));
    localStorage.setItem('user.emailSettings', JSON.stringify(user.emailSettings));
}

function Display({state}: {state: {user: User, isLoading: boolean}}): JSX.Element {
    if(state.isLoading && !state.user.email) {
        return LoadingScreen()
    } else {
        return ShowForm(state.user)
    }
}

function LoadingScreen(): JSX.Element {
    return (
        <div>Loading...</div>
    )
}

function ShowForm(user: User): JSX.Element {
    return (
        <UserSettingsForm user={user} submitRequest={updateUser}>
            <DeleteUserButton onClick={triggerDeleteUser(user)}>Delete Account</DeleteUserButton>
        </UserSettingsForm>
    )
}

function triggerDeleteUser(user: User): (e: React.MouseEvent) => void {
    return (e: React.MouseEvent) => {
        if(window.confirm("Are you sure you want to delete your account?")) {
            deleteUser(user)
        }
    }
}

export default EditUser