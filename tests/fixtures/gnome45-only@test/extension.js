import Clutter from 'gi://Clutter';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class Gnome45OnlyExtension extends Extension {
    enable() {
        this._box.add_actor(new Clutter.Actor());
        let color = new Clutter.Color({red: 255});
    }

    disable() {
        this._box = null;
    }
}
