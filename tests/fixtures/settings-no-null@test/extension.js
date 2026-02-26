import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class SettingsLeakExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._handler = this._settings.connect('changed', () => {});
    }
    disable() {
        this._settings.disconnect(this._handler);
        // Forgot to null _settings
    }
}
