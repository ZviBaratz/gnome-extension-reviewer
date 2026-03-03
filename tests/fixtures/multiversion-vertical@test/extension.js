import St from 'gi://St';
import Clutter from 'gi://Clutter';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class MultiVersionExtension extends Extension {
    enable() {
        this._box = new St.BoxLayout({vertical: true});
        this._box.vertical = false;
    }

    disable() {
        this._box.destroy();
        this._box = null;
    }
}
