import Adw from 'gi://Adw';
// Bug: wrong case — should be /Shell/Extensions/ (capitalized)
import {ExtensionPreferences} from 'resource:///org/gnome/shell/extensions/prefs.js';

export default class TestPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const page = new Adw.PreferencesPage();
        window.add(page);
    }
}
