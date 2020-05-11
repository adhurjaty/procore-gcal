import User from "../models/user"

export function getUserSettings(userId: string): User {
    let response = {
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