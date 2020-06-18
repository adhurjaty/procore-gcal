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

async function sendRequest(req: Request): Promise<any> {
    console.log(req.url);
    console.log(API_USER('blah'));
    const response = await fetch(withTokenHeader(req));
    return await response.json();
}

async function sendStatusRequest(req: Request): Promise<StatusMessage> {
    const data = await sendRequest(req)
    return {
        status: data.status,
        message: data.message
    };
}

export async function getUserSettings(userId: string): Promise<User> {
    const response = await sendRequest(new Request(API_USER(userId), {
        method: 'GET'
    }));
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
        id: id,
        name: 'Carl Contractor',
        email: 'ccontractor@example.com'
    };

    let c = new Collaborator(collab);
    return c;
}

export async function createNewUser(user: User) : Promise<StatusMessage> {
    return sendStatusRequest(new Request(API_NEW_USER, {
        method: 'POST',
        body: JSON.stringify(user.toJson())
    }));
}

export async function updateUser(user: User) : Promise<StatusMessage> {
    return sendStatusRequest(new Request(API_USER(user.id), {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(user.toJson()),
    }));
}

export async function deleteUser(user: User) : Promise<StatusMessage> {
    return sendStatusRequest(new Request(API_USER(user.id), {
        method: 'DELETE'
    }));
}

export async function createCollaborator(collaborator: Collaborator): 
    Promise<StatusMessage>
{
    return sendStatusRequest(new Request(API_NEW_COLLABORATOR('' + collaborator.id), {
        method: 'POST',
        body: JSON.stringify(collaborator.json())
    }));
}