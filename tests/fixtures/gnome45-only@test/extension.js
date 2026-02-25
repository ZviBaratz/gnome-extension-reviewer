import Clutter from 'gi://Clutter';
import Shell from 'gi://Shell';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class Gnome45OnlyExtension extends Extension {
    enable() {
        this._box.add_actor(new Clutter.Actor());
        let color = new Clutter.Color({red: 255});
        this._blur = new Shell.BlurEffect({sigma: 20});
        this._box.vertical = true;
    }

    disable() {
        this._box = null;
    }
}
