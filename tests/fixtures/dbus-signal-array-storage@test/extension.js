import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

export default class extends Extension {
    enable() {
        this._proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION, 0, null,
            'org.freedesktop.DBus', '/org/freedesktop/DBus',
            'org.freedesktop.DBus', null);
        this._signalIds = [];
        this._signalIds.push(this._proxy.connectSignal('NameOwnerChanged', () => {}));
        this._signalIds.push(
            this._proxy.connectSignal('NameAcquired', () => {})
        );
    }
    disable() {
        this._signalIds.forEach(id => this._proxy.disconnectSignal(id));
        this._signalIds = null;
        this._proxy = null;
    }
}
