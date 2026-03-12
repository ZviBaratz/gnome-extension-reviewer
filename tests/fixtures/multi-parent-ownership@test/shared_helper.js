export class SharedHelper {
    constructor() {
        this._handlerId = global.display.connect('notify::focus-window', () => {});
    }

    disconnect_all() {
        if (this._handlerId) {
            global.display.disconnect(this._handlerId);
            this._handlerId = null;
        }
    }
}
