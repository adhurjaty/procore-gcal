import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const FlashContainer = styled.div`
    border-radius: 5px;
    padding-top: 10px;
    padding-bottom: 10px;
    width: 100%;
    justify-content: center;
    align-content: center;
    border-style: solid;
    border-width: 2px;
`;

const SuccessContainer = styled(FlashContainer)`
    background-color: #8bc34a;
    border-color: green;
`;

const ErrorContainer = styled(FlashContainer)`
    background-color: #ff6666;
    border-color: red;
`;

export default function Flash({visibility, isSuccess, message}: 
    {visibility: boolean, isSuccess: boolean, message: string}) : JSX.Element
{
    const content = (
        isSuccess ? <SuccessContainer>{message}</SuccessContainer>
            : <ErrorContainer>{message}</ErrorContainer>
    );
    return (
        visibility ? content : <div></div>
    )
}