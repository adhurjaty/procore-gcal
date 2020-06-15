import { UserItem } from "./interfaces";

export default class Collaborator {
    id: string = "";
    email: string = "";
    name: string = "";
    isPending: boolean = true;

    constructor()
    constructor(object: UserItem)
    constructor(object?: UserItem) {
        if(object) {
            this.id = object.id;
            this.name = object.name;
            this.email = object.email;
        }
    }

    copy(): Collaborator {
        return new Collaborator({id: this.id, email: this.email, name: this.name});
    }

    json(): UserItem {
        return {
            id: this.id,
            name: this.name,
            email: this.email
        };
    }
}