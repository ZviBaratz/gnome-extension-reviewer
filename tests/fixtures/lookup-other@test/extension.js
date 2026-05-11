import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class LookupOtherExtension extends Extension {
    enable() {
        // Cross-extension lookup — should be flagged
        const other = Extension.lookupByUUID('other-extension@example.com');
        other?.someMethod();
    }

    disable() {}
}
