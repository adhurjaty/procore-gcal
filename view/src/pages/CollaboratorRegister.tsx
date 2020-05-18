import React, { useState, useEffect } from 'react'
import styled from 'styled-components';
import { Heading, SettingsForm, InputSection, InputLabel, FieldError } from '../components/GlobalStyles';
import GCalButton from '../components/GCalButton';
import { useParams } from 'react-router-dom';
import { getCollaborator, createCollaborator } from '../backend_interface/api_interface';
import Collaborator from '../models/collaborator';
import { GCAL_COLLABORATOR_LOGIN_URL } from '../AppSettings';

enum PageStateEnum {
    Loading,
    CollabForm,
    Success,
    AlreadyRegistered
}

interface PageState {
    state: PageStateEnum,
    collaborator: Collaborator | null,
    managerName: string
};

const Container = styled.div`
    display: flex;
    flex-direction: column;
`

const SubmitButton = styled.button`
    align-self: flex-end;
    margin-right: 30px;
`

const CenterContainer = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
`

function CollaboratorRegister(): JSX.Element {
    const initState: PageState = {
        state: PageStateEnum.Loading,
        collaborator: null,
        managerName: ""
    }

    const {collaboratorId} = useParams();
    const [pageState, setPageState] = useState(initState);

    useEffect(() => {
        getCollaborator(collaboratorId).then((collab) => {
            if(collab.isPending) {
                setPageState(Object.assign({}, pageState, {
                    state: PageStateEnum.CollabForm,
                    collaborator: collab
                }));
            } else {
                setPageState(Object.assign({}, pageState, {
                    state: PageStateEnum.AlreadyRegistered
                }));
            }
        });
    }, [])

    return (
        <Container>
            <Heading>Collaborator Registration</Heading>
            <PageContents state={pageState} setState={setPageState} />
        </Container>
    )
}

function PageContents({state, setState}: {state: PageState, setState: (s: PageState) => void}):
    JSX.Element
{
    switch (state.state) {
        case PageStateEnum.Loading:
            return <LoadingPage />
        case PageStateEnum.CollabForm:
            return <CollaboratorForm state={state} setState={setState} />
        case PageStateEnum.Success:
            return <SuccessPage />
        case PageStateEnum.AlreadyRegistered:
            return <AlreadyRegisteredPage />
        default:
            throw new Error("Invalid page state");
    }
}

function LoadingPage(): JSX.Element {
    return (
        <h4>Loading collaborator info...</h4>
        // TODO: put in loading spinner
    )
}

function CollaboratorForm({state, setState}: {state: PageState, setState: (s: PageState) => void}):
    JSX.Element
{
    const [nameError, setNameError] = useState("");
    const [collaborator, setCollaborator] = useState(state.collaborator as Collaborator);

    useEffect(() => {
        if(state.collaborator)
            setCollaborator(state.collaborator as Collaborator)
    }, [state]);

    const validate = () => {
        if(!state.collaborator) {
            throw new Error("Missing collaborator");
        }

        if(!/[\w\-_ ]+/.test(state.collaborator.name)) {
            setNameError("Must enter a name");
            return false;
        }

        return true;
    };

    const handleSubmit = (evt: React.MouseEvent) => {
        if(!validate()) {
            return;
        }

        let collaborator = state.collaborator as Collaborator
        createCollaborator(collaborator).then((resp) => {
            if(resp.status === 'error') {
                setNameError(resp.message);
            } else {
                setState(Object.assign({}, state, {state: PageStateEnum.Success}));
            }
        });
    }

    return (
        <SettingsForm>
            <EmailSection email={collaborator.email} />
            <NameSection collab={collaborator} error={nameError} />
            <InputSection>
                <GCalButton loginUrl={GCAL_COLLABORATOR_LOGIN_URL('' + collaborator.id)} />
            </InputSection>
            <SubmitButton onClick={handleSubmit}>Submit</SubmitButton>
        </SettingsForm>
    )
}

function EmailSection({email}: {email: string}): JSX.Element {
    return (
        <InputSection>
            <InputLabel>Email:</InputLabel>
            <div>{email}</div>
        </InputSection>
    );
}

function NameSection({collab, error}: {collab: Collaborator, error: string}): JSX.Element {
    const [name, setName] = useState(collab.name);
    useEffect(() => {
        collab.name = name;
    }, [name]);

    return (
        <InputSection>
            <InputLabel>Full Name:</InputLabel>
            <input 
                type="text" 
                value={name}
                onChange={e => setName(e.target.value)} />
            <FieldError>{error}</FieldError>
        </InputSection>
    );
}

function SuccessPage(): JSX.Element {
    return (
        <CenterContainer>
            <h4>Success</h4>

        </CenterContainer>
    )
}

function AlreadyRegisteredPage(): JSX.Element {
    return (
        <CenterContainer>
            <div>User has already been registered</div>
        </CenterContainer>
    )
}

export default CollaboratorRegister