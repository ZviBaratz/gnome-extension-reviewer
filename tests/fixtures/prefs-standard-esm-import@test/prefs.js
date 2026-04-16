import Adw from 'gi://Adw';
// Standard ESM framework import — this must NOT trigger imports/resource-path-case
import {ExtensionPreferences} from 'resource:///org/gnome/shell/extensions/prefs.js';

export default class TestPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const page = new Adw.PreferencesPage();
        window.add(page);
    }
}
