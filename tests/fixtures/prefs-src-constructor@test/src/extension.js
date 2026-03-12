import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        this._enabled = true;
    }

    disable() {
        this._enabled = false;
    }
}
