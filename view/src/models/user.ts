import NamedItem from "./namedItem";
import EventType from "./eventType";
import EmailSetting from "./emailSetting";
import Collaborator from "./collaborator";
import { SelectableItem, UserItem } from "./interfaces";

interface CollaboratorResponse {
    name: string
};

interface UserResponse {
    id?: string,
    email: string,
    fullName: string,
    calendars: NamedItem[],
    selectedCalendar: number,
    eventTypes: SelectableItem[],
    collaborators: UserItem[],
    emailSettings: SelectableItem[],
    isSubscribed: boolean;
    projectId: number | null;
    projects: NamedItem[]
};

export default class User {
    id: string = "";
    email: string = "";
    fullName: string = "";
    selectedCalendar: NamedItem | undefined = undefined;
    calendars: NamedItem[] = [];
    projectId: number | null = null;
    projects: NamedItem[] = [];
    eventTypes: EventType[] = [];
    collaborators: Collaborator[] = [];
    emailSettings: EmailSetting[] = [];
    isSubscribed: boolean = false;
    
    static fromJSON(response: UserResponse): User {
        let user = new User();
        user.id = response.id ?? "";
        user.email = response.email;
        user.fullName = response.fullName;
        user.calendars = response.calendars;
        user.selectedCalendar = user.calendars.find(c => c.id == response.selectedCalendar);
        user.eventTypes = response.eventTypes.map(x => new EventType(x));
        user.collaborators = response.collaborators.map(x => new Collaborator(x));
        user.emailSettings = response.emailSettings.map(x => new EmailSetting(x));
        user.isSubscribed = response.isSubscribed;
        user.projectId = response.projectId;
        user.projects = response.projects;

        return user;
    }

    toJson() {
        return {
            id: this.id,
            email: this.email,
            fullName: this.fullName,
            selectedCalendar: (this.selectedCalendar as NamedItem).id,
            projectId: this.projectId,
            eventTypes: this.eventTypes.map(x => x.json()),
            collaborators: this.collaborators.map(x => x.json()),
            emailSettings: this.emailSettings.map(x => x.json()),
            isSubscribed: this.isSubscribed
        }
    }
}