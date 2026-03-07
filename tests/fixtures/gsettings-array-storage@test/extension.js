import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class ArrayStorageExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._signalIds = [];
        this._signalIds.push(this._settings.connect('changed::interval', () => this._onChanged()));
        this._signalIds.push(
            this._settings.connect('changed::mode', () => this._onMode()),
        );
    }

    _onChanged() {}
    _onMode() {}

    disable() {
        this._signalIds.forEach(id => this._settings.disconnect(id));
        this._signalIds = [];
        this._settings = null;
    }
}
