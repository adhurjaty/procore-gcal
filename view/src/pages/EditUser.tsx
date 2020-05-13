import React from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom'
import { getUserSettings, updateUser, deleteUser } from '../backend_interface/api_interface';
import UserSettingsForm from '../components/UserSettingsForm';

const DeleteUserButton = styled.button`
    background-color: red
`

function EditUser(): JSX.Element {
    let { userId } = useParams();
    const user = getUserSettings(userId);

    const triggerDeleteUser = (e: React.MouseEvent) => {
        if(window.confirm("Are you sure you want to delete your account?")) {
            deleteUser(user)
        }
    }

    return (
        <UserSettingsForm user={user} submitRequest={updateUser}>
            <DeleteUserButton onClick={triggerDeleteUser}>Delete Account</DeleteUserButton>
        </UserSettingsForm>
    )
}

export default EditUser