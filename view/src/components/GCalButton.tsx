import React from 'react';
import styled from 'styled-components';


const ButtonBase = ({href, className=''}: {href: string, className?: string}) => (
    <a href={href} className={"button " + className} />
);

const StyledButton = styled(ButtonBase)`
    background-image: url("${process.env.PUBLIC_URL}/btn_google_signin_dark_normal_web.png");
    width: 191px;
    height: 45px;
`;

export function GCalButton({loginUrl}: {loginUrl: string}) {
    return (
        <StyledButton href={loginUrl} />
    )
}

export default GCalButton
