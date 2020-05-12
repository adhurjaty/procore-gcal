import React, { useState } from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom'
import { getUserSettings } from '../backend_interface/api_interface';
import Calendar from '../models/caldendar';
import GCalButton from '../components/GCalButton';


const Container = styled.div`
    display: flex;
    flex-direction: column;
`

const Heading = styled.h2`
    align-self: center;
`

const SettingsForm = styled.form`
    display: flex;
    flex-direction: column;
    align-items: flex-start;
`

const InputSection = styled.div`
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-top: 10px;
    margin-bottom: 10px;
    margin-left: 20px;
`

const InputLabel = styled.label`
    font-weight: bold;
    font-size: 14px;
    margin-bottom: 5px;
`

const FieldError = styled.div`
    color: red;
    margin-top: 5px;
`

function UserSettings(): JSX.Element {
    let { userId } = useParams();
    const user = getUserSettings(userId);

    const handleSubmit = (evt: React.FormEvent<HTMLFormElement>) => {
        evt.preventDefault();
    }

    const [fullName, setFullName] = useState(user.fullName);
    const [selectedCalendar, setSelectedCalendar] = useState(user.selectedCalendar);
    const [eventTypes, setEventTypes] = useState(user.eventTypes);
    const [collaborators, setCollaborators] = useState(user.collaborators);
    const [emailSettings, setEmailSettings] = useState(user.emailSettings);
    const [isSubscribed, setSubscribed] = useState(user.isSubscribed);
    
    return (
        <Container>
            <Heading>User Settings</Heading>
            <SettingsForm onSubmit={handleSubmit}>
                <InputSection>
                    <InputLabel>Email:</InputLabel>
                    <div>{user.email}</div>
                </InputSection>
                <InputSection>
                    <InputLabel>Full Name:</InputLabel>
                    <input 
                        type="text" 
                        value={fullName}
                        onChange={e => setFullName(e.target.value)} />
                </InputSection>
                <InputSection>
                    <InputLabel>Google Calendar:</InputLabel>
                    {user.calendars && selectedCalendar
                        ? renderCalendars(user.calendars, selectedCalendar, setSelectedCalendar)
                        : renderGCalButton()}
                </InputSection>
            </SettingsForm>
        </Container>
    )
}

function renderCalendars(calendars: Calendar[], selectedCalendar: Calendar, 
    setSelectedCalendar: (c: Calendar) => void) 
{
    const onSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newCal = calendars.find(c => c.id == parseInt(e.target.value));
        setSelectedCalendar(newCal as Calendar);
    }
    return (
        <select onChange={onSelect}>
            {calendars.map((c, i) => {
                const isSelected = selectedCalendar.id === c.id;
                return (
                    <option key={`${c.id}-${i}`}
                        value={c.id}
                        selected={isSelected}>
                        {c.name}
                    </option>
                )
            })}
        </select>
    )
}

const ButtonContainer = styled.div`
    display: flex;
    justify-content: center;
`

function renderGCalButton() {
    return (
        <ButtonContainer>
            <GCalButton />
        </ButtonContainer>
    )
}

export default UserSettings