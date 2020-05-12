import React from 'react';
import styled from 'styled-components';
import {GCAL_LOGIN_URL} from '../AppSettings';


const ButtonBase = ({href, className=''}: {href: string, className?: string}) => (
    <a href={href} className={"button " + className} />
);

const StyledButton = styled(ButtonBase)`
    background-image: url("${process.env.PUBLIC_URL}/btn_google_signin_dark_normal_web.png");
    width: 191px;
    height: 45px;
`;

function GCalButton() {
    return (
        <StyledButton href={GCAL_LOGIN_URL} />
    )
}

export default GCalButton
