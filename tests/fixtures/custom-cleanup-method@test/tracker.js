export class SignalTracker {
    constructor() {
        this._handlers = [];
    }

    track(obj, signal) {
        const id = obj.connect(signal, () => {});
        this._handlers.push({obj, id});
    }

    disconnect_all() {
        for (const {obj, id} of this._handlers) {
            obj.disconnect(id);
        }
        this._handlers = [];
    }
}
