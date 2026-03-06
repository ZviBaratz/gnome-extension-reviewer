import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

export default class DbusLeakExtension extends Extension {
    enable() {
        this._proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION, 0, null,
            'org.mpris.MediaPlayer2', '/org/mpris/MediaPlayer2',
            'org.mpris.MediaPlayer2.Player', null);
        this._proxy.connectSignal('PropertiesChanged', () => this._onProps());
        this._proxy.connectSignal('Seeked', () => this._onSeek());
    }

    _onProps() {}
    _onSeek() {}

    disable() {
        this._proxy = null;
    }
}
