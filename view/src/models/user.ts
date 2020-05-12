import Calendar from "./caldendar";
import EventType from "./eventType";
import EmailSetting from "./emailSetting";
import Collaborator from "./collaborator";
import { SelectableItem, NamedItem } from "./interfaces";

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
        user.eventTypes = response.eventTypes.map(x => new EventType(x));
        user.collaborators = response.collaborators.map(x => new Collaborator(x));
        user.isSubscribed = response.isSubscribed;

        return user;
    }
}