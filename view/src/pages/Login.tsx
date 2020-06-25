import React from 'react'
import styled from 'styled-components'
import { PROCORE_LOGIN_URL } from '../AppSettings';

const Container = styled.div`
    display: flex;
    flex-direction: column;
    align-self: center;
    padding: 10px;
    max-width: 600px;
`;

const TextDiv = styled.div`
    text-align: left;
`;

function Login(): JSX.Element {
    return (
        <Container>
            <TextDiv>
                <p>Welcome to the Procore Calendar Integrator. <br/>
                    Please click the 'Procore Login' button to login or sign up.</p>
            </TextDiv>
            <a className="procore-button button" href={PROCORE_LOGIN_URL}>
                Procore Login
            </a>
        </Container>
    )
}

export default Login;