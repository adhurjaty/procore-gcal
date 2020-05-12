import { NamedItem } from "./interfaces";

export default class Collaborator {
    id: number = -1;
    name: string = "";

    constructor()
    constructor(object: NamedItem)
    constructor(object?: NamedItem) {
        if(object) {
            this.id = object.id;
            this.name = object.name;
        }
    }

    copy(): Collaborator {
        return new Collaborator({id: this.id, name: this.name});
    }
}