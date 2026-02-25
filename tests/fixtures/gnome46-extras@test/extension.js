import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Shell from 'gi://Shell';
import Clutter from 'gi://Clutter';

export default class Gnome46ExtrasTest extends Extension {
    enable() {
        this._blur = new Shell.BlurEffect({sigma: 20});
        this._blur.sigma = 30;
        // Clutter.Container interface removed in GNOME 46
        const iface = Clutter.Container;
    }

    disable() {
        this._blur = null;
    }
}
