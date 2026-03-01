import Adw from 'gi://Adw';
import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class TestPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const page = new Adw.PreferencesPage();
        const group = new Adw.PreferencesGroup();
        const row = new Adw.SwitchRow({title: 'Enable feature'});
        row.connect('notify::active', () => {
            this._settings.set_boolean('enabled', row.active);
        });
        group.add(row);
        page.add(group);
        window.add(page);
    }
}
