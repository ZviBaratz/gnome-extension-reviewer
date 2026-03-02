import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import GLib from 'gi://GLib';

// Class with destroy() that calls .disconnect() — lifecycle-managed
class ManagedPanel {
    constructor(settings) {
        this._settings = settings;
        this._handlerId = settings.connect('changed', () => {});
        this._timeout = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, () => {
            return GLib.SOURCE_REMOVE;
        });
    }
    destroy() {
        this._settings.disconnect(this._handlerId);
        GLib.source_remove(this._timeout);
    }
}

// Class with disable() cleanup — also lifecycle-managed
class DisabledPanel {
    constructor(settings) {
        this._id = settings.connect('changed::key', () => {});
    }
    disable() {
        this._settings.disconnect(this._id);
    }
}

// Class using connectObject — auto-managed by GObject lifecycle
class ObjectPanel {
    constructor(source) {
        source.connectObject('notify::visible', () => {}, this);
    }
}

// Prototype injection — no enclosing class, should be skipped
const OverrideCommon = {
    _init() {
        this._handlerId = this.connect('button-press-event', () => {});
    },
};

export default class ManagedExtension extends Extension {
    enable() {
        this._panel = new ManagedPanel(this.getSettings());
    }
    disable() {
        this._panel.destroy();
        this._panel = null;
    }
}
