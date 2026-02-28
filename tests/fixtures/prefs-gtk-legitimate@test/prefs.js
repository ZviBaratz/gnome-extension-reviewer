import Adw from 'gi://Adw';
import Gtk from 'gi://Gtk';
import { ExtensionPreferences } from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class TestPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const page = new Adw.PreferencesPage();
        const group = new Adw.PreferencesGroup();

        // Replaceable: should be blocking (R-PREFS-04)
        const header = new Gtk.HeaderBar({});

        // Advisory: has Adw replacement (R-PREFS-04b)
        const combo = new Gtk.ComboBoxText({});
        const expander = new Gtk.Expander({ label: 'More' });

        // Advisory: legitimate GTK layout widget (R-PREFS-04c)
        const scroll = new Gtk.ScrolledWindow({});

        page.add(group);
        window.add(page);
    }
}
