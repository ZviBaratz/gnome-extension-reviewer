export class Manager {
    enable() {
        this._handlerId = global.display.connect('window-created', () => {});
    }

    disable() {
        global.display.disconnect(this._handlerId);
        this._handlerId = null;
    }
}
