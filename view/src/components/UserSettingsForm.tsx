import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom'
import { getUserSettings } from '../backend_interface/api_interface';
import Calendar from '../models/caldendar';
import GCalButton from './GCalButton';
import EventType from '../models/eventType';
import User from '../models/user';
import Enablable from '../models/Enablable';
import Collaborator from '../models/collaborator';
import { PayPalButton } from "react-paypal-button-v2";
import { API_USER } from '../AppSettings';


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

const MinusInputContainer = styled.div`
    display: flex;
    flex-direction: row;
`

const InlineButton = styled.button`
    padding-bottom: 2px;
`

const SubmitButton = styled.button`
    align-self: flex-end;
    margin-right: 30px;
`

function UserSettingsForm({user, submitRequest, children}: 
    {user: User, submitRequest: (user: User) => Request, children?: React.ReactNode}): 
    JSX.Element 
{
    const [fullNameError, setFullNameError] = useState("");
    const [calendarError, setCalendarError] = useState("");
    const [collaboratorError, setCollaboratorError] = useState("");
    const [subscribeError, setSubscribeError] = useState("");

    const initSubscribed = user.isSubscribed;

    const validate = () => {
        if(!/[\w\-_ ]+/.test(user.fullName)) {
            setFullNameError("Must enter a full name");
            return false;
        }
        if(!user.selectedCalendar) {
            setCalendarError("Must select a calendar");
            return false;
        }
        // TODO: collaborator error check
        // TODO: subscribe error check

        return true;
    };
    
    const handleSubmit = (evt: React.MouseEvent) => {
        if(!validate()) {
            return;
        }

        fetch(submitRequest(user))
            .then((resp) => {
                // TODO: show success
            })
            .catch((reason) => {
                // TODO: show failure
            });
    }
    
    return (
        <Container>
            <Heading>User Settings</Heading>
            <SettingsForm onSubmit={e => e.preventDefault()}>
                <EmailSection user={user} />
                <NameSection user={user} error={fullNameError} />
                <CalendarSection user={user} error={calendarError} />
                <EventTypesSection user={user} />
                <CollaboratorSection user={user} error={collaboratorError} />
                <EmailSettingsSection user={user} />
                {!initSubscribed && 
                    <SubscriptionSection user={user} error={subscribeError} />}

                {children}

                <SubmitButton onClick={handleSubmit}>Submit</SubmitButton>
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
    useEffect(() => {
        user.fullName = fullName;
    });

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
    useEffect(() => {
        user.selectedCalendar = selectedCalendar;
    });

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
        const newCal = calendars.find(c => c.id === parseInt(e.target.value));
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

    useEffect(() => {
        user.eventTypes = eventTypes;
    })

    const checkFn = onCheckedFn(eventTypes, setEventTypes);

    return (
        <InputSection>
            <InputLabel>Event Types:</InputLabel>
            {eventTypes.map((et, i) => (
                <Checkbox onChange={checkFn(et)}
                    key={`${et.id}-${i}`}
                    label={et.name} 
                    checked={et.enabled} />
            ))}
        </InputSection>
    );
}

function Checkbox({checked, onChange, label}: {checked: boolean, 
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void, label: string}):
    JSX.Element
{
    return (
        <label>
            <input type="checkbox"
                onChange={onChange}
                checked={checked} />
            <span className="checkable">{label}</span>
        </label>
    );
}

function onCheckedFn(checkFields: Enablable[], 
    setCheckFields: (fields: Enablable[]) => void) : 
    (field: Enablable) => (e: React.ChangeEvent<HTMLInputElement>) => void
{
    return (field: Enablable) => (e: React.ChangeEvent<HTMLInputElement>) => {
        setCheckFields(checkFields.map((et, i) => {
            if(field === et) {
                let newEvent = et.copy();
                newEvent.enabled = e.target.checked;
                return newEvent;
            }
            return et;
        }));
    }
}

function CollaboratorSection({user, error}: {user: User, error: string}): JSX.Element {
    const [collaborators, setCollaborators] = useState(user.collaborators);

    useEffect(() => {
        user.collaborators = collaborators;
    })

    const entryUpdated = (collab: Collaborator) => 
        (e: React.ChangeEvent<HTMLInputElement>) => 
    {
        setCollaborators(collaborators.map(c => {
            if(c.id === collab.id) {
                let newC = c.copy();
                newC.name = e.target.value;
                return newC;
            }
            return c;
        }))
    }

    const removeEntry = (collab: Collaborator) => (_: React.MouseEvent) => {
        setCollaborators(collaborators.filter(c => c !== collab));
    }

    const addEntry = (_: React.MouseEvent) => {
        setCollaborators(collaborators.concat(new Collaborator()))
    }

    return (
        <InputSection>
            <InputLabel>Collaborators (max 5):</InputLabel>
            {collaborators.map((c, i) => {
                let key = `${c.id}-${i}`;
                return (
                    <MinusInput key={key} 
                        value={c.name}
                        onChange={entryUpdated(c)}
                        onClick={removeEntry(c)} />
                );
            })}
            {collaborators.length < 5 && <PlusButton onClick={addEntry} />}
            <FieldError>{error}</FieldError>
        </InputSection>
    )
}

function MinusInput({value, onChange, onClick}: {value: string, 
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void, 
    onClick: (e: React.MouseEvent) => void}): JSX.Element
{
    return (
        <MinusInputContainer>
            <input type="text"
                value={value}
                onChange={onChange} />
            <MinusButton onClick={onClick} />
        </MinusInputContainer>
    );
}

function MinusButton({onClick}: {onClick: (e: React.MouseEvent) => void}): JSX.Element {
    return (
        <InlineButton onClick={onClick}>-</InlineButton>
    );
}

function PlusButton({onClick}: {onClick: (e: React.MouseEvent) => void}): JSX.Element {
    return (
        <button onClick={onClick}>+</button>
    );
}

function EmailSettingsSection({user}: {user: User}): JSX.Element {
    const [emailSettings, setEmailSettings] = useState(user.emailSettings);

    useEffect(() => {
        user.emailSettings = emailSettings;
    })

    const checkFn = onCheckedFn(emailSettings, setEmailSettings);

    return (
        <InputSection>
            <InputLabel>Email Notification Settings:</InputLabel>
            {emailSettings.map((es, i) => (
                <Checkbox onChange={checkFn(es)}
                    key={`${es.id}-${i}`}
                    label={es.name} 
                    checked={es.enabled} />
            ))}
        </InputSection>
    );
}

function SubscriptionSection({user, error}: {user: User, error: string}): JSX.Element
{
    const [isSubscribed, setSubscribed] = useState(user.isSubscribed);

    useEffect(() => {
        user.isSubscribed = isSubscribed;
    });

    const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSubscribed(!isSubscribed);
    }
    
    return (
        <InputSection>
            <InputLabel>Subsrciption:</InputLabel>
            <RadioButton checked={!isSubscribed} 
                onChange={onChange}
                label="Free Trial (1 month)" />
            <RadioButton checked={isSubscribed} 
                onChange={onChange}
                label="Subscription" />
            <br/>
            {isSubscribed && <PayPalButton amount="0.01" />}
            <FieldError>{error}</FieldError>
        </InputSection>
    );
}

function RadioButton({checked, onChange, label}: {checked: boolean, 
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void, label: string}):
    JSX.Element
{
    return (
        <label>
            <input type="radio"
                onChange={onChange}
                checked={checked} />
            <span className="checkable">{label}</span>
        </label>
    );
}

export default UserSettingsForm