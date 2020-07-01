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
    padding-left: 2%;
    padding-right: 2%;
    height: 50px;
    background: rgb(220,220,220);
    align-items: center;
`;

function Header(): JSX.Element {
    return (
        <NavBar>
            <span><b>Procore Calendar Integrator</b></span>
            {IsLoggedIn() &&
                <a className="pseudo button" 
                    href="/"
                    onClick={(e) => LogOut()}>
                    Log Out
                </a>
            }
        </NavBar>
    )
}

export default Header