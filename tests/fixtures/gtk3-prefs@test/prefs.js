import Gtk from 'gi://Gtk';
import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class Gtk3PrefsExtension extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const box = new Gtk.Box({orientation: Gtk.Orientation.VERTICAL});
        const label = new Gtk.Label({label: 'Settings'});
        box.append(label);
    }
}
