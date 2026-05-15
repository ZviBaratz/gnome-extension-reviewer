import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// Opens an external app via GDesktopAppInfo. The desktop file ID is a
// reverse-DNS identifier ending in .desktop — not an extension API call.
export default class TestExtension extends Extension {
    enable() {
        // Desktop file IDs used as app identifiers — not extension API calls
        const apps = [
            'com.mattjakeman.ExtensionManager.desktop',
            'org.gnome.Extensions.desktop',
        ];
    }
    disable() {}
}
