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
        user: new User(),
        isLoading: true
    };
    const [state, setState] = useState(initState)

    useEffect(() => {
        getUserSettings(userId).then((user) => {
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

function Display({state}: {state: {user: User, isLoading: boolean}}): JSX.Element {
    if(state.isLoading) {
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