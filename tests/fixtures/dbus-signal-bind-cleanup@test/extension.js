import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

export default class extends Extension {
    enable() {
        this._proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION, 0, null,
            'org.mpris.MediaPlayer2', '/org/mpris/MediaPlayer2',
            'org.mpris.MediaPlayer2.Player', null);
        this._seekedId = this._proxy.connectSignal('Seeked', () => {});
        this._cleanups = [
            this._proxy.disconnectSignal.bind(this._proxy, this._seekedId),
        ];
    }

    disable() {
        this._cleanups.forEach(cb => cb());
        this._cleanups = null;
        this._proxy = null;
    }
}
