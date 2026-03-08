import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class CrossFileLeakExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._settings.connect('changed::interval', () => this._onChanged());
        this._settings.connect('changed::mode', () => this._onMode());
    }

    _onChanged() {}
    _onMode() {}

    disable() {
        this._settings = null;
    }
}
