import styled from 'styled-components';


export const Heading = styled.h2`
    align-self: center;
`

export const InputSection = styled.div`
    display: flex;
    flex-flow: column;
    align-items: flex-start;
    flex-basis: 45%;
    margin-top: 10px;
    margin-bottom: 10px;
    margin-left: 20px;
    min-width: 250px;
`

export const InputLabel = styled.label`
    font-weight: bold;
    font-size: 14px;
    margin-bottom: 5px;
`

export const FieldError = styled.div`
    color: red;
    margin-top: 5px;
`