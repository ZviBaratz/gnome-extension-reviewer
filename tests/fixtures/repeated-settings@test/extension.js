import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class RepeatedSettingsExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._settings2 = this.getSettings();
    }

    disable() {
        this._settings = null;
        this._settings2 = null;
    }
}
