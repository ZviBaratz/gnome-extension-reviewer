// Base class providing enable/disable lifecycle for the extension.
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

export class BaseExtension extends Extension {
    enable() {
        // base enable logic
    }

    disable() {
        // base disable logic
    }
}
