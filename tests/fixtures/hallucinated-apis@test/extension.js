import Meta from 'gi://Meta';
import St from 'gi://St';
import GLib from 'gi://GLib';
import Clutter from 'gi://Clutter';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class HallucinatedExtension extends Extension {
    enable() {
        const screen = Meta.Screen.get_default();
        St.Label.set_text(this._label, 'hello');
        Clutter.Actor.show_all();
        GLib.source_remove(this._id);
        if (typeof super.destroy === 'function') super.destroy();
        if (this instanceof HallucinatedExtension) {}
    }

    disable() {}
}
