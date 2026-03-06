import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class AutoCleanupExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._settings.connect('changed::interval', () => this._onChanged());
    }

    _onChanged() {}

    disable() {
        this._settings.disconnectObject(this);
        this._settings = null;
    }
}
