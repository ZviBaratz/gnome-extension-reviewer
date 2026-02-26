import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

export default class TestExtension extends Extension {
    enable() {
        Gio._promisify(Gio.File.prototype, 'load_contents_async');
        this._settings = this.getSettings();
    }

    disable() {
        this._settings = null;
    }
}
