import Adw from 'gi://Adw';
import Gtk from 'gi://Gtk';

// WRONG: both prefs methods defined
class MyPrefs {
    getPreferencesWidget() {
        return new Gtk.Label({label: 'test'});
    }
    fillPreferencesWindow(window) {
        const page = new Adw.PreferencesPage();
        window.add(page);
    }
}
