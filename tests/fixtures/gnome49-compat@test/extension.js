import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Meta from 'gi://Meta';
import Clutter from 'gi://Clutter';

export default class Gnome49Test extends Extension {
    enable() {
        let rect = new Meta.Rectangle({x: 0, y: 0, width: 100, height: 100});
        this._click = new Clutter.ClickAction();
        this._tap = new Clutter.TapAction();
    }

    disable() {
        this._click = null;
        this._tap = null;
    }
}
