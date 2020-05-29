import { SelectableItem } from "./interfaces";


export default abstract class Enablable {
    id: number = 0;
    name: string = "";
    enabled: boolean = false;

    constructor()
    constructor(obj: SelectableItem)
    constructor(obj?: SelectableItem) {
        if(obj) {
            this.name = obj.name;
            this.enabled = obj.enabled;
        }
    }

    abstract copy(): Enablable;

    json(): SelectableItem {
        return {
            name: this.name,
            enabled: this.enabled
        };
    }
}