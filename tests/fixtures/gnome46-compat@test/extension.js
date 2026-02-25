import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class Gnome46CompatExtension extends Extension {
    enable() {
        this._box.add_actor(new Clutter.Actor());
        this._box.remove_actor(this._child);
    }

    disable() {
        this._box = null;
    }
}
