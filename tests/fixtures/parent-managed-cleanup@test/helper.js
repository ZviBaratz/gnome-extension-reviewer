export class SignalHelper {
    connect_all() {
        this._handlerId = global.display.connect('window-created', () => {});
    }

    disconnect_all() {
        if (this._handlerId) {
            global.display.disconnect(this._handlerId);
            this._handlerId = null;
        }
    }
}
