import Adw from 'gi://Adw';
import Gtk from 'gi://Gtk';
import { ExtensionPreferences } from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class TestPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const page = new Adw.PreferencesPage();
        const group = new Adw.PreferencesGroup();

        // Replaceable: should be blocking (R-PREFS-04)
        const list = new Gtk.ListBox({});
        const header = new Gtk.HeaderBar({});

        // Legitimate: should be advisory (R-PREFS-04b)
        const label = new Gtk.SpinButton({});
        const button = new Gtk.Button({ label: 'Click' });

        page.add(group);
        window.add(page);
    }
}
