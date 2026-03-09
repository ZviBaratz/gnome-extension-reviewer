import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class ArrayLiteralExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._signalIds = [
            this._settings.connect('changed::interval', () => this._onChanged()),
            this._settings.connect('changed::mode', () => this._onMode()),
            this._settings.connect('changed::level', () => this._onLevel()),
        ];
    }

    _onChanged() {}
    _onMode() {}
    _onLevel() {}

    disable() {
        this._signalIds.forEach(id => this._settings.disconnect(id));
        this._signalIds = [];
        this._settings = null;
    }
}
