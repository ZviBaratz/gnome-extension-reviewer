import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class BusNameLeakExtension extends Extension {
    enable() {
        // BAD: owns a bus name but never releases it
        this._ownerId = Gio.bus_own_name(
            Gio.BusType.SESSION,
            'org.example.MyExtension',
            Gio.BusNameOwnerFlags.NONE,
            null, null, null
        );
    }

    disable() {
        // Missing: Gio.bus_unown_name(this._ownerId)
        this._ownerId = null;
    }
}
