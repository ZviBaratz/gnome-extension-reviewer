import Gtk from 'gi://Gtk';
import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class Gtk3PrefsExtension extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const grid = new Gtk.Grid({column_spacing: 12});
        const label = new Gtk.Label({label: 'Settings'});
        grid.attach(label, 0, 0, 1, 1);
    }
}
