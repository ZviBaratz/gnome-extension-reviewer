import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class SchemaTest extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._val = this._settings.get_boolean('enabled');
        this._changedId = this._settings.connect('changed::refresh-interval', () => this._refresh());
    }
    _refresh() {
        const interval = this._settings.get_int('refresh-interval');
    }
    disable() {
        this._settings.disconnect(this._changedId);
        this._settings = null;
    }
}
