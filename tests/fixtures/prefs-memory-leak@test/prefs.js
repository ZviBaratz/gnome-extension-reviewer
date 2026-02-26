import Gio from 'gi://Gio';
import Adw from 'gi://Adw';
import { ExtensionPreferences } from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class TestPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        this._settings = new Gio.Settings({ schemaId: this.metadata['settings-schema'] });
        this._page = new Adw.PreferencesPage();
        window.add(this._page);
    }
}
