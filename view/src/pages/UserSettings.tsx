import React, { useState } from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom'
import { getUserSettings } from '../backend_interface/api_interface';
import Calendar from '../models/caldendar';
import GCalButton from '../components/GCalButton';
import EventType from '../models/eventType';
import User from '../models/user';


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

const CalendarSelector = styled.select`
    min-width: 200px;
`;

const ButtonContainer = styled.div`
    display: flex;
    justify-content: center;
`

function UserSettings(): JSX.Element {
    let { userId } = useParams();
    const user = getUserSettings(userId);

    const handleSubmit = (evt: React.FormEvent<HTMLFormElement>) => {
        evt.preventDefault();
    }

    const [fullNameError, setFullNameError] = useState("");
    const [calendarError, setCalendarError] = useState("");
    const [collaborators, setCollaborators] = useState(user.collaborators);
    const [collaboratorError, setCollaboratorError] = useState("");
    const [emailSettings, setEmailSettings] = useState(user.emailSettings);
    const [isSubscribed, setSubscribed] = useState(user.isSubscribed);
    
    return (
        <Container>
            <Heading>User Settings</Heading>
            <SettingsForm onSubmit={handleSubmit}>
                <EmailSection user={user} />
                <NameSection user={user} error={fullNameError} />
                <CalendarSection user={user} error={calendarError} />
                <EventTypesSection user={user} />
            </SettingsForm>
        </Container>
    )
}

function EmailSection({user}: {user: User}): JSX.Element {
    return (
        <InputSection>
            <InputLabel>Email:</InputLabel>
            <div>{user.email}</div>
        </InputSection>
    );
}

function NameSection({user, error}: {user: User, error: string}): JSX.Element {
    const [fullName, setFullName] = useState(user.fullName);

    return (
        <InputSection>
            <InputLabel>Full Name:</InputLabel>
            <input 
                type="text" 
                value={fullName}
                onChange={e => setFullName(e.target.value)} />
            <FieldError>{error}</FieldError>
        </InputSection>
    );
}

function CalendarSection({user, error}: {user: User, error: string}): JSX.Element {
    const [selectedCalendar, setSelectedCalendar] = useState(user.selectedCalendar);

    return (
        <InputSection>
            <InputLabel>Google Calendar:</InputLabel>
            {user.calendars && selectedCalendar
                ? renderCalendars(user.calendars, selectedCalendar, setSelectedCalendar)
                : renderGCalButton()}
            <FieldError>{error}</FieldError>
        </InputSection>
    );
}

function renderCalendars(calendars: Calendar[], selectedCalendar: Calendar, 
    setSelectedCalendar: (c: Calendar) => void) 
{
    const onSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newCal = calendars.find(c => c.id == parseInt(e.target.value));
        setSelectedCalendar(newCal as Calendar);
    }
    return (
        <CalendarSelector onChange={onSelect}>
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
        </CalendarSelector>
    );
}

function renderGCalButton(): React.ReactNode {
    return (
        <ButtonContainer>
            <GCalButton />
        </ButtonContainer>
    );
}

function EventTypesSection({user}: {user: User}): JSX.Element {
    const [eventTypes, setEventTypes] = useState(user.eventTypes);

    return (
        <InputSection>
            <InputLabel>Event Types:</InputLabel>
            {eventTypes.map((et, i) => (
                <Checkbox onChange={onEventTypeCheckedFn(eventTypes, setEventTypes)}
                    id={et.id}
                    key={`${et.id}${i}`}
                    label={et.name} 
                    checked={et.enabled} />
            ))}
        </InputSection>
    );
}

function Checkbox({checked, onChange, label, id}: {checked: boolean, 
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void, label: string, id: number}):
    JSX.Element
{
    return (
        <label>
            <input type="checkbox"
                onChange={onChange}
                checked={checked}
                name={`${id}`} />
            <span className="checkable">{label}</span>
        </label>
    );
}

function onEventTypeCheckedFn(eventTypes: EventType[], 
    setEventTypes: (types: EventType[]) => void) : 
    (e: React.ChangeEvent<HTMLInputElement>) => void
{
    return (e: React.ChangeEvent<HTMLInputElement>) => {
        setEventTypes(eventTypes.map((et, i) => {
            if(et.id == parseInt(e.target.name)) {
                let newEvent = et.copy();
                newEvent.enabled = e.target.checked;
                return newEvent;
            }
            return et;
        }));
    }
}

export default UserSettings