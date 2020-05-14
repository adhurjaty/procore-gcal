import React from 'react'
import styled from 'styled-components';
import { Heading, SettingsForm, InputSection, InputLabel } from '../components/GlobalStyles';
import GCalButton from '../components/GCalButton';
import { useParams } from 'react-router-dom';
import { getCollaborator } from '../backend_interface/api_interface';

const Container = styled.div`
    display: flex;
    flex-direction: column;
`

function CollaboratorRegister(): JSX.Element {
    const {collaboratorId} = useParams();
    const collaborator = getCollaborator(collaboratorId);

    return (
        <Container>
            <Heading>Collaborator Registration</Heading>
            <SettingsForm>
                <EmailSection email={collaborator.email} />
                <GCalButton />
            </SettingsForm>
        </Container>
    )
}

function EmailSection({email}: {email: string}): JSX.Element {
    return (
        <InputSection>
            <InputLabel>Email:</InputLabel>
            <div>{email}</div>
        </InputSection>
    );
}

export default CollaboratorRegister