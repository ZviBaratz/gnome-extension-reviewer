import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class SchemaTest extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._val = this._settings.get_int('real-key');
        this._bad = this._settings.get_string('phantom-key');
    }
    disable() {
        this._settings = null;
    }
}
