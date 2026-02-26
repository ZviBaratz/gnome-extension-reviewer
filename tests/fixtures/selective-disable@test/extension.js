import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        this._indicator = new Object();
    }

    disable() {
        if (this._enabled) return;
        this._indicator = null;
    }
}
