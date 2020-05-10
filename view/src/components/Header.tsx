import React from 'react'
import styled from 'styled-components'

const HeaderRow = styled.header`
    display: flex;
    justify-content: center;
`

function Header(): JSX.Element {
    return (
        <HeaderRow><h1>Procore Google Calendar Integrator</h1></HeaderRow>
    )
}

export default Header