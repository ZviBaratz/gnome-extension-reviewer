import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// Module-scope data container — not a resource
const HEADER = new GLib.Bytes('header data');

export default class MyExtension extends Extension {
    enable() {
        this._data = HEADER;
    }

    disable() {
        this._data = null;
    }
}
