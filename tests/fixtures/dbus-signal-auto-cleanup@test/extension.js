import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

export default class DbusAutoCleanupExtension extends Extension {
    enable() {
        this._proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION, 0, null,
            'org.mpris.MediaPlayer2', '/org/mpris/MediaPlayer2',
            'org.mpris.MediaPlayer2.Player', null);
        this._proxy.connectSignal('PropertiesChanged', () => this._onProps());

        this._settings = this.getSettings();
        this._settings.connectObject('changed::mode', () => {}, this);
    }

    _onProps() {}

    disable() {
        this._settings.disconnectObject(this);
        this._proxy = null;
        this._settings = null;
    }
}
