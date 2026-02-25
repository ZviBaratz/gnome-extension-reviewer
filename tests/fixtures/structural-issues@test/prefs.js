import Adw from 'gi://Adw';
import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class TestPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        console.log('debug info');
    }
}
