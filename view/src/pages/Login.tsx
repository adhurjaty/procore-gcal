import React from 'react'
import styled from 'styled-components'
import { PROCORE_LOGIN_URL } from '../AppSettings';

const ButtonContainer = styled.div`
    display: flex;
    justify-content: center;
    margin-top: 200px;
`


function Login(): JSX.Element {
    return (
        <ButtonContainer>
            <a className="procore-button button" href={PROCORE_LOGIN_URL}>
                Procore Login
            </a>
        </ButtonContainer>
    )
}

export default Login;