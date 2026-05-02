import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

class Timeouts {
    constructor() {
        this.store = new Map();
    }

    register(sourceId) {
        const key = `timer-${GLib.uuid_string_random()}`;
        this.store.set(key, sourceId);
        return key;
    }

    idle(callback) {
        return this.register(
            GLib.idle_add(GLib.PRIORITY_DEFAULT, () => {
                callback.call(null);
                return GLib.SOURCE_REMOVE;
            })
        );
    }

    timeout(time, callback) {
        return this.register(
            GLib.timeout_add(GLib.PRIORITY_DEFAULT, time, () => {
                callback.call(null);
                return GLib.SOURCE_REMOVE;
            })
        );
    }

    removeAll() {
        for (const [key, sourceId] of this.store) {
            GLib.Source.remove(sourceId);
            this.store.delete(key);
        }
    }
}

export default class WrapperTrackedExt extends Extension {
    enable() {
        this._timeouts = new Timeouts();
        this._timeouts.timeout(1000, () => this._doStuff());
    }

    _doStuff() {}

    disable() {
        this._timeouts.removeAll();
        this._timeouts = null;
    }
}
