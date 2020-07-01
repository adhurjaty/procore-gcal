import React from 'react'
import styled from 'styled-components'
import { LogOut, IsLoggedIn } from '../util/helpers';

const HeaderRow = styled.header`
    display: flex;
    justify-content: center;
`

const NavBar = styled.div`
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding-left: 20px;
    padding-right: 2%;
    height: 50px;
    align-items: center;
    margin-bottom: 10px;
`;

const LogoutButton = styled.a`
    font-size: 0.95em;
`

function Header(): JSX.Element {
    return (
        <NavBar>
            <span><b>Procore Calendar Integrator</b></span>
            {IsLoggedIn() &&
                <LogoutButton className="pseudo button" 
                    href="/"
                    onClick={(e) => LogOut()}>
                    Log Out
                </LogoutButton>
            }
        </NavBar>
    )
}

export default Header