export class SignalTracker {
    constructor() {
        this._connections = [];
    }

    connectSmart(obj, signal, callback) {
        const id = obj.connect(signal, callback);
        this._connections.push({obj, id});
        return id;
    }

    disconnectSmart() {
        for (const {obj, id} of this._connections)
            obj.disconnect(id);
        this._connections = [];
    }
}
