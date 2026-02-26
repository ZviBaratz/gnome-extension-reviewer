import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

let proxy = new Gio.DBusProxy();

export default class ModuleScopeExtension extends Extension {
    enable() {
        this._data = proxy.get_cached_property('SomeProperty');
    }

    disable() {
        this._data = null;
    }
}
