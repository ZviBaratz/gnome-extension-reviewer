import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';
import {buildPrefsPage} from './lib/prefsHelper.js';
import {getVersion} from './lib/shared.js';

export default class ImportGraphPrefs extends ExtensionPreferences {
    getPreferencesWidget() {
        return buildPrefsPage(this.getSettings());
    }
}
