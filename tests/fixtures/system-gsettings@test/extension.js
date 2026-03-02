import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        // Accessing a system schema — should NOT trigger R-SLOP-24
        this._mutter = new Gio.Settings({schema: 'org.gnome.mutter'});
    }

    disable() {
        this._mutter = null;
    }
}
