import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Meta from 'gi://Meta';
import Clutter from 'gi://Clutter';

export default class Gnome49Test extends Extension {
    enable() {
        let rect = new Meta.Rectangle({x: 0, y: 0, width: 100, height: 100});
        this._click = new Clutter.ClickAction();
        this._tap = new Clutter.TapAction();
    }

    // Ternary version-compat guard: should NOT trigger R-VER49-08/11
    _maximizeCompat(window) {
        window.get_maximized ? window.maximize(Meta.MaximizeFlags.BOTH) : window.maximize();
    }

    _unmaximizeCompat(window) {
        window.get_maximized ? window.unmaximize(Meta.MaximizeFlags.BOTH) : window.unmaximize();
    }

    disable() {
        this._click = null;
        this._tap = null;
    }
}
