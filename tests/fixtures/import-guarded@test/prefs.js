import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';
import * as utils from './utils.js';

export default class GuardedPrefs extends ExtensionPreferences {
    async fillPreferencesWindow(window) {
        // Prefs-only import via guard — safe, Shell process gets null
        const Gtk = await utils.importInPrefsOnly('gi://Gtk');
        if (Gtk) {
            const box = new Gtk.Box();
            window.add(box);
        }
    }
}
