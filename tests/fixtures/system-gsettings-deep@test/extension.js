import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class DeepSchemaExtension extends Extension {
    enable() {
        // System schema with comments pushing schema to line+4
        this._bg = new Gio.Settings({
            // Desktop background settings
            // Used for wallpaper management
            // across multiple monitors
            schema: 'org.gnome.desktop.background',
        });
    }

    disable() {
        this._bg = null;
    }
}
