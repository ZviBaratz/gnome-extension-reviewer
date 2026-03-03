import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class MultilineSchemaExtension extends Extension {
    enable() {
        // Multi-line constructor with schema_id on next line
        this._mutter = new Gio.Settings({
            schema_id: 'org.gnome.mutter'
        });

        // Multi-line with schema on line after that
        this._desktop = new Gio.Settings({
            schema_id: 'org.gnome.desktop.interface',
        });

        // Keybinding constant reference
        this._keys = new Gio.Settings({
            schema_id: WindowManager.SHELL_KEYBINDINGS_SCHEMA,
        });
    }

    disable() {
        this._mutter = null;
        this._desktop = null;
        this._keys = null;
    }
}
