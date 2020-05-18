import User from "../models/user"
import EventType from "../models/eventType";
import EmailSetting from "../models/emailSetting";
import { API_NEW_USER, API_USER, API_NEW_COLLABORATOR } from "../AppSettings";
import Collaborator from "../models/collaborator";

const TOKEN_COOKIE_NAME = 'auth_token'

export interface StatusMessage {
    status: string,
    message: string
}

export function getToken() {
    return document.cookie
        .split(';')
        .map(c => c.trim())
        .find(c => c.startsWith(`${TOKEN_COOKIE_NAME}=`));
}

function setToken() {

}

function withTokenHeader(req: Request): Request {
    req.headers.append('Authorization', `Bearer ${getToken()}`);
    return req;
}

async function sendRequest(req: Request): Promise<StatusMessage> {
    const response = await fetch(withTokenHeader(req));
    const data = await response.json();
    return {
        status: data.status,
        message: data.message
    };
}

export function getUserSettings(userId: string): User {
    let response = {
        id: 4,
        email: "adhurjaty@gmail.com",
        fullName: "Anil Dhurjaty",
        calendars: [
            {
                name: "Personal Calendar",
                id: 0
            },
            {
                name: "Other Calendar",
                id: 1
            }
        ],
        selectedCalendar: 0,
        eventTypes: [
            {
                id: 0,
                name: "RFIs",
                enabled: true,
            },
            {
                id: 1,
                name: "Submittals",
                enabled: true,
            },
            {
                id: 2,
                name: "Change Orders",
                enabled: false,
            }
        ],
        collaborators: [],
        emailSettings: [
            {
                id: 0,
                name: "Google Calendar Events",
                enabled: true
            },
            {
                id: 1,
                name: "Add/Remove Caldendar",
                enabled: false
            },
            {
                id: 2,
                name: "User Updates",
                enabled: false
            },
        ],
        isSubscribed: false
    }

    return User.fromJSON(response);
}

export function getEventTypes(): EventType[] {
    let eventTypes = [
        {
            id: 0,
            name: "RFIs",
            enabled: false,
        },
        {
            id: 1,
            name: "Submittals",
            enabled: false,
        },
        {
            id: 2,
            name: "Change Orders",
            enabled: false,
        }
    ];
    return eventTypes.map(x => new EventType(x));
}

export function getEmailSettings(): EmailSetting[] {
    let emailSettings = [
        {
            id: 0,
            name: "Google Calendar Events",
            enabled: false
        },
        {
            id: 1,
            name: "Add/Remove Caldendar",
            enabled: false
        },
        {
            id: 2,
            name: "User Updates",
            enabled: false
        },
    ];
    return emailSettings.map(x => new EmailSetting(x));
}

export async function getCollaborator(id: string): Promise<Collaborator> {
    let collab = {
        id: parseInt(id),
        name: 'Carl Contractor',
        email: 'ccontractor@example.com'
    };

    let c = new Collaborator(collab);
    return c;
}

export async function createNewUser(user: User) : Promise<StatusMessage> {
    return sendRequest(new Request(API_NEW_USER, {
        method: 'POST',
        body: JSON.stringify(user.toJson())
    }));
}

export async function updateUser(user: User) : Promise<StatusMessage> {
    return sendRequest(new Request(API_USER('' + user.id), {
        method: 'PATCH',
        body: JSON.stringify(user.toJson()),
    }));
}

export async function deleteUser(user: User) : Promise<StatusMessage> {
    return sendRequest(new Request(API_USER('' + user.id), {
        method: 'DELETE'
    }));
}

export async function createCollaborator(collaborator: Collaborator): 
    Promise<StatusMessage>
{
    return sendRequest(new Request(API_NEW_COLLABORATOR('' + collaborator.id), {
        method: 'POST',
        body: JSON.stringify(collaborator.json())
    }));
}