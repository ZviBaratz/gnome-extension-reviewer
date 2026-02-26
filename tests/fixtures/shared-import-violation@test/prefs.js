import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';
import {makeLabel} from './utils.js';

export default class SharedImportPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const label = makeLabel('Settings');
    }
}
