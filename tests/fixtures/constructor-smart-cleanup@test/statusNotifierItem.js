export class StatusNotifierItem {
    constructor(settings) {
        // Resources in constructor — but class uses connectSmart for cleanup
        this._settings = settings;
        this._id = settings.connect('changed', () => this._update());
        this.connectSmart(settings, 'changed::theme', () => this._refresh());
    }

    connectSmart(obj, signal, callback) {
        this._smartIds = this._smartIds || [];
        this._smartIds.push({obj, id: obj.connect(signal, callback)});
    }

    disconnectSmart() {
        for (const {obj, id} of this._smartIds || [])
            obj.disconnect(id);
        this._smartIds = [];
    }

    _update() {}
    _refresh() {}
}
