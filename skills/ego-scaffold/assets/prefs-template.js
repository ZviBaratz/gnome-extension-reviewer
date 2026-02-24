import Adw from 'gi://Adw';
import Gio from 'gi://Gio';
import Gtk from 'gi://Gtk';

import {ExtensionPreferences, gettext as _} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class ${CLASS_NAME}Preferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings();

        const page = new Adw.PreferencesPage({
            title: _('General'),
            icon_name: 'preferences-system-symbolic',
        });
        window.add(page);

        const group = new Adw.PreferencesGroup({
            title: _('Settings'),
            description: _('Configure ${NAME}'),
        });
        page.add(group);

        // TODO: Add preference rows here
        // Example:
        // const row = new Adw.SwitchRow({
        //     title: _('Enable Feature'),
        //     subtitle: _('Toggle this feature on or off'),
        // });
        // settings.bind('feature-enabled', row, 'active', Gio.SettingsBindFlags.DEFAULT);
        // group.add(row);
    }
}
