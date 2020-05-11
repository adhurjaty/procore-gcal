import Calendar from "./caldendar";
import EventType from "./eventType";
import EmailSetting from "./emailSetting";
import Collaborator from "./collaborator";

interface NamedItem {
    id: number,
    name: string
};

interface SelectableItem {
    id: number,
    name: string,
    enabled: boolean
};

interface CollaboratorResponse {
    name: string
};

interface UserResponse {
    email: string,
    fullName: string,
    calendars: NamedItem[],
    selectedCalendar: number,
    eventTypes: SelectableItem[],
    collaborators: NamedItem[],
    emailSettings: SelectableItem[],
    isSubscribed: boolean;
};

export default class User {
    email: string = "";
    fullName: string = "";
    selectedCalendar: Calendar | undefined = undefined;
    calendars: Calendar[] = [];
    eventTypes: EventType[] = [];
    collaborators: Collaborator[] = [];
    emailSettings: EmailSetting[] = [];
    isSubscribed: boolean = false;
    
    static fromJSON(response: UserResponse): User {
        let user = new User();
        user.email = response.email;
        user.fullName = response.fullName;
        user.calendars = response.calendars;
        user.selectedCalendar = user.calendars.find(c => c.id == response.selectedCalendar);
        user.eventTypes = response.eventTypes;
        user.collaborators = response.collaborators;
        user.isSubscribed = response.isSubscribed;

        return user;
    }
}