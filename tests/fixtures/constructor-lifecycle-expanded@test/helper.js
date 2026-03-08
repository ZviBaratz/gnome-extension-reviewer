import Clutter from 'gi://Clutter';
import GLib from 'gi://GLib';

// Class with _destroy() cleanup — should suppress constructor-resources
class PrivateDestroyPanel {
    constructor(settings) {
        this._settings = settings;
        this._handlerId = settings.connect('changed', () => {});
    }
    _destroy() {
        this._settings.disconnect(this._handlerId);
    }
}

// Class with onDestroy() cleanup — should suppress constructor-resources
class OnDestroyPanel {
    constructor(settings) {
        this._settings = settings;
        this._id = settings.connect('changed::key', () => {});
    }
    onDestroy() {
        this._settings.disconnect(this._id);
    }
}

// Effect subclass — should suppress constructor-resources (widget base)
class CustomEffect extends Clutter.ShaderEffect {
    constructor() {
        super();
        this.connect('notify::enabled', () => {});
    }
}

export {PrivateDestroyPanel, OnDestroyPanel, CustomEffect};
