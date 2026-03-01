import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class DBusSyncExtension extends Extension {
    enable() {
        const bus = Gio.DBus.system;
        // BAD: synchronous D-Bus call blocks compositor
        const result = bus.call_sync(
            'org.freedesktop.UPower',
            '/org/freedesktop/UPower',
            'org.freedesktop.DBus.Properties',
            'Get',
            null, null, Gio.DBusCallFlags.NONE, -1, null
        );
        this._result = result;
    }

    disable() {
        this._result = null;
    }
}
