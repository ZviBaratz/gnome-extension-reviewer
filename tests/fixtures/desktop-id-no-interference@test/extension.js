import Gtk from 'gi://Gtk';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {ExtensionPreferences} from 'resource:///org/gnome/shell/extensions/prefs.js';

// Opens an external app via GDesktopAppInfo. The desktop file ID is a
// reverse-DNS identifier ending in .desktop — not an extension API call.
export default class TestExtension extends Extension {
    enable() {}
    disable() {}
}

export class Prefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const combo = new Gtk.ComboBoxText();
        combo.append('com.mattjakeman.ExtensionManager.desktop', 'Extensions Manager');
        combo.append('org.gnome.Extensions.desktop', 'Extensions');
    }
}
