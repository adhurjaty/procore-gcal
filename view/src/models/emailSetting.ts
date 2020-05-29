import Enablable from "./Enablable";

export default class EmailSetting extends Enablable {

    copy() {
        return new EmailSetting({
            name: this.name,
            enabled: this.enabled
        });
    }
}