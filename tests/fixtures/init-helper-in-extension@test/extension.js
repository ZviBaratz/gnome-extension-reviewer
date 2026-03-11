import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import Gio from 'gi://Gio';

// Helper class — instantiated at runtime from enable()
class Helper {
    constructor() {
        this._cancellable = new Gio.Cancellable();
    }
    destroy() {
        this._cancellable.cancel();
        this._cancellable = null;
    }
}

export default class TestExtension extends Extension {
    constructor(metadata) {
        super(metadata);
        // VIOLATION: Shell global in Extension constructor
        this._hasOverview = Main.sessionMode.hasOverview;
    }

    enable() {
        this._helper = new Helper();
    }

    disable() {
        this._helper.destroy();
        this._helper = null;
    }
}
