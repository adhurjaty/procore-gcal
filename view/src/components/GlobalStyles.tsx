import styled from 'styled-components';


export const Heading = styled.h2`
    align-self: center;
`

export const SettingsForm = styled.form`
    display: flex;
    flex-direction: column;
    align-items: flex-start;
`

export const InputSection = styled.div`
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-top: 10px;
    margin-bottom: 10px;
    margin-left: 20px;
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