import React from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom'


const Container = styled.div`
    display: flex;
    flex-direction: column;
`

const Heading = styled.h2`
    align-self: center;
`

const SettingsForm = styled.form`
    display: flex;
    flex-direction: column;
    align-items: flex-start;
`

const InputSection = styled.div`
    display: flex;
    flex-direction: column;
    margin-top: 10px;
    margin-bottom: 10px;
    margin-left: 20px;
`

const InputLabel = styled.label`
    font-weight: bold;
    font-size: 14px;
`

function UserSettings(): JSX.Element {
    let { userId } = useParams();

    return (
        <Container>
            <Heading>User Settings</Heading>
            <SettingsForm>
                <InputSection>
                    <InputLabel>Email:</InputLabel>

                </InputSection>
            </SettingsForm>
        </Container>
    )
}

export default UserSettings