import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class ValidTestExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
    }

    disable() {
        this._settings = null;
    }
}
