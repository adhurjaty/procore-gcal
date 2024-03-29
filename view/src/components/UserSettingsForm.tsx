import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom'
import { getUserSettings, StatusMessage, getToken } from '../backend_interface/api_interface';
import NamedItem from '../models/namedItem';
import GCalButton from './GCalButton';
import EventType from '../models/eventType';
import User from '../models/user';
import Enablable from '../models/Enablable';
import Collaborator from '../models/collaborator';
import { PayPalButton } from "react-paypal-button-v2";
import { API_USER, GCAL_USER_LOGIN_URL } from '../AppSettings';
import { Heading, InputSection, InputLabel, FieldError } from './GlobalStyles';
import Flash from './Flash';

const Container = styled.div`
    display: flex;
    flex-direction: column;
    align-self: center;
    padding: 10px;
    max-width: 600px;
    @media (min-width: 700px) {
        border: 1px solid lightgray;
        border-radius: 25px;
    }
`

const ItemSelector = styled.select`
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

const SubmitButtonContainer = styled.div`
    display: flex;
    flex-direction: row;
    justify-content: center;
    margin-top: 30px;
`

const SectionsContainer = styled.div`
    display: flex;
    flex-flow: row wrap;
    justify-content: space-between;
    align-items: flex-start;
    margin-left: 20px;
    margin-right: 20px;
`

const ChildrenContainer = styled.div`
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    margin-left: 20px;
    margin-right: 20px;
`

// TODO: add storing form values into local storage

function UserSettingsForm({user, submitRequest, children}: {user: User, 
    submitRequest: (user: User) => Promise<StatusMessage>, children?: React.ReactNode}): 
    JSX.Element 
{
    const [fullNameError, setFullNameError] = useState("");
    const [calendarError, setCalendarError] = useState("");
    const [collaboratorError, setCollaboratorError] = useState("");
    const [subscribeError, setSubscribeError] = useState("");
    const [successMessage, setSuccessMessage] = useState("");
    const [requestErrorMessage, setRequestErrorMessage] = useState("");

    const initSubscribed = user.isSubscribed;

    const validate = () => {
        setFullNameError('');
        setCalendarError('');

        if(!/[\w\-_ ]+/.test(user.fullName.trim())) {
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
        setRequestErrorMessage('');
        setSuccessMessage('');

        if(!validate()) {
            return;
        }

        storeValues(user);

        submitRequest(user)
            .then((result) => {
                if(result.status === 'error') {
                    setRequestErrorMessage(result.message);
                } else {
                    setSuccessMessage(result.message);
                    window.scrollTo(0, 0);
                }
            })
            .catch((error: Error) => {
                setRequestErrorMessage("Not authorized - please refresh the page");
            });
    }
    
    return (
        <Container>
            <Heading>User Settings</Heading>
            <Flash visibility={!!successMessage} 
                   isSuccess={true} 
                   message={successMessage} />
            <form onSubmit={e => e.preventDefault()}>
                <SectionsContainer>
                    <EmailSection user={user} />
                    <NameSection user={user} error={fullNameError} />
                    <ProjectsSection user={user} />
                    <CalendarSection user={user} error={calendarError} />
                    <EventTypesSection user={user} />
                    {/* <CollaboratorSection user={user} error={collaboratorError} /> */}
                    <EmailSettingsSection user={user} />
                    {!initSubscribed && 
                        <SubscriptionSection user={user} error={subscribeError} />
                    }
                </SectionsContainer>

                <ChildrenContainer>
                    {children}
                </ChildrenContainer>

                <Flash visibility={!!requestErrorMessage} 
                       isSuccess={false} 
                       message={requestErrorMessage} />
                <SubmitButtonContainer>
                    <button onClick={handleSubmit}>Submit</button>
                </SubmitButtonContainer>
            </form>
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
    }, [fullName]);

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

function ProjectsSection({user}: {user: User}): JSX.Element {
    const initProject = user.projects.find(x => x.id == user.projectId) 
        ?? user.projects.find(x => true);
    const [selectedProject, setSelectedProject] = useState(initProject)

    useEffect(() => {
        if(selectedProject) {
            user.projectId = selectedProject.id as number;
        }
    }, [selectedProject])

    return (
        <InputSection>
            <InputLabel>Procore Projects:</InputLabel>
            {!!selectedProject 
                ? renderNamedDropdown(user.projects, selectedProject, setSelectedProject)
                : emptyProjectsMessage()
            }
        </InputSection>
    )
}

function emptyProjectsMessage(): JSX.Element {
    return (
        <div>You are not part of any Procore projects</div>
    )
}

function CalendarSection({user, error}: {user: User, error: string}): JSX.Element {
    let initCalendar = user.selectedCalendar;
    const [selectedCalendar, setSelectedCalendar] = useState(initCalendar);
    useEffect(() => {
        user.selectedCalendar = selectedCalendar;
    }, [selectedCalendar]);
    useEffect(() => {
        setSelectedCalendar(initCalendar);
    }, [initCalendar]);

    return (
        <InputSection>
            <InputLabel>Google Calendar:</InputLabel>
            {user.calendars && selectedCalendar
                ? renderNamedDropdown(user.calendars, selectedCalendar, setSelectedCalendar)
                : renderGCalButton(user)}
            <FieldError>{error}</FieldError>
        </InputSection>
    );
}

function renderNamedDropdown(items: NamedItem[], selectedItem: NamedItem, 
    setSelectedItem: (c: NamedItem) => void) 
{
    const onSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newCal = items.find(c => c.id == e.target.value);
        setSelectedItem(newCal as NamedItem);
    }

    return (
        <ItemSelector onChange={onSelect} value={selectedItem.id}>
            {items.map((c, i) => {
                return (
                    <option key={`${c.id}-${i}`}
                        value={c.id}>
                        {c.name}
                    </option>
                )
            })}
        </ItemSelector>
    );
}

function renderGCalButton(user: User): React.ReactNode {
    return (
        <ButtonContainer>
            <GCalButton loginUrl={GCAL_USER_LOGIN_URL(getToken() as string)} 
                onClick={() => storeValues(user)}/>
        </ButtonContainer>
    );
}

function storeValues(user: User) {
    localStorage.setItem('user.fullName', user.fullName);
    localStorage.setItem('user.projectId', '' + user.projectId);
    if(user.selectedCalendar)
        localStorage.setItem('user.selectedCalendar', user.selectedCalendar.id as string);
    localStorage.setItem('user.eventTypes', JSON.stringify(user.eventTypes));
    localStorage.setItem('user.emailSettings', JSON.stringify(user.emailSettings));
}

function EventTypesSection({user}: {user: User}): JSX.Element {
    const [eventTypes, setEventTypes] = useState(user.eventTypes);

    useEffect(() => {
        user.eventTypes = eventTypes;
    }, [eventTypes])

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
                let newEvent = (et as Enablable).copy();
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
    }, [collaborators])

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
    }, [emailSettings]);

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
    }, [isSubscribed]);

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