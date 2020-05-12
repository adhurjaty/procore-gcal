import Enablable from "./Enablable";

export default class EventType extends Enablable {
    copy(): EventType {
        return new EventType(this);
    }
}