import React from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom'
import { getUserSettings } from '../backend_interface/api_interface';
import { API_USER } from '../AppSettings';
import UserSettingsForm from '../components/UserSettingsForm';
import User from '../models/user';

const DeleteUserButton = styled.button`
    background-color: red
`

function EditUser(): JSX.Element {
    let { userId } = useParams();
    const user = getUserSettings(userId);

    const requestFn = (user: User) => {
        return new Request(API_USER(userId), {
            method: 'PATCH',
            body: JSON.stringify(user.toJson())
        });
    };

    const deleteUser = (e: React.MouseEvent) => {
        debugger;
        if(window.confirm("Are you sure you want to delete your account?")) {
            fetch(new Request(API_USER(userId), {
                method: 'DELETE'
            }));
        }
    }

    return (
        <UserSettingsForm user={user} submitRequest={requestFn}>
            <DeleteUserButton onClick={deleteUser}>Delete Account</DeleteUserButton>
        </UserSettingsForm>
    )
}

export default EditUser