import React from 'react';
import styled from 'styled-components';


const ButtonBase = ({href, className='', onClick=() => {}}: 
    {href: string, className?: string, onClick?: () => void}) => 
(
    <a href={href} 
        className={"button " + className}
        onClick={onClick} />
);

const StyledButton = styled(ButtonBase)`
    background-image: url("${process.env.PUBLIC_URL}/btn_google_signin_dark_normal_web.png");
    width: 191px;
    height: 45px;
`;

export function GCalButton({loginUrl, onClick=() => {}}: 
    {loginUrl: string, onClick?: () => void}) 
{
    return (
        <StyledButton href={loginUrl} onClick={onClick} />
    )
}

export default GCalButton
