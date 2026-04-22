import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// GNOME 49+ conditional import — init-only, not mutable app state
let GioUnix;
try {
    GioUnix = (await import('gi://GioUnix?version=2.0')).default;
} catch {}

export default class ConditionalImportExtension extends Extension {
    enable() {
        // GioUnix may be undefined on older GNOME versions
        if (GioUnix) {
            // use it
        }
    }

    disable() {}
}
