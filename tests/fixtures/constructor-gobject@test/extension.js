import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Pango from 'gi://Pango';

export default class ConstructorGObjectExtension extends Extension {
    constructor(metadata) {
        super(metadata);
        // BAD: GObject creation in constructor
        this._file = new Gio.File.new_for_path('/tmp/test');
        this._variant = new GLib.Variant('s', 'test');
        this._layout = new Pango.Layout(null);
    }

    enable() {
        this._settings = this.getSettings();
    }

    disable() {
        this._settings = null;
    }
}
