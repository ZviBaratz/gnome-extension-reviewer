import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const NOTIFICATIONS_SCHEMA = 'org.gnome.desktop.notifications';

export default class BareSchemaExtension extends Extension {
    enable() {
        // Bare system schema substring — should NOT trigger R-SLOP-24
        this._iface = new Gio.Settings({
            schema_id: 'desktop.interface',
        });

        // _SCHEMA constant — should NOT trigger R-SLOP-24
        this._notif = new Gio.Settings({
            schema_id: NOTIFICATIONS_SCHEMA,
        });

        // Bare shell system schema — should NOT trigger R-SLOP-24
        this._switcher = new Gio.Settings({
            schema_id: 'shell.app-switcher',
        });

        // Extension-owned schema — SHOULD trigger R-SLOP-24
        this._own = new Gio.Settings({
            schema_id: 'org.gnome.shell.extensions.myext',
        });
    }

    disable() {
        this._iface = null;
        this._notif = null;
        this._switcher = null;
        this._own = null;
    }
}
