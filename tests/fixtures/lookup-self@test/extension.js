import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class LookupSelfExtension extends Extension {
    enable() {
        // Self-lookup for openPreferences from a menu button — legitimate pattern
        const self = Extension.lookupByUUID('lookup-self@test');
        self?.openPreferences();
    }

    disable() {}
}
