import { SelectableItem } from "./interfaces";

export default class EventType {
    id: number = 0;
    name: string = "";
    enabled: boolean = false;

    constructor()
    constructor(obj: SelectableItem)
    constructor(obj?: SelectableItem) {
        if(obj) {
            this.id = obj.id;
            this.name = obj.name;
            this.enabled = obj.enabled;
        }
    }

    public copy(): EventType {
        return new EventType(this);
    }
}