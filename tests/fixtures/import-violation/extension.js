import Gtk from 'gi://Gtk';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class ImportViolationExtension extends Extension {
    enable() {
        this._label = new Gtk.Label({label: 'Bad import'});
    }

    disable() {
        this._label = null;
    }
}
