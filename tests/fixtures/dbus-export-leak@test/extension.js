import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const IfaceXml = `
<node>
  <interface name="org.example.Test">
    <method name="DoSomething"/>
  </interface>
</node>`;

export default class DBusLeakExtension extends Extension {
    enable() {
        this._dbus = Gio.DBusExportedObject.wrapJSObject(IfaceXml, this);
        this._dbus.export(Gio.DBus.session, '/org/example/Test');
    }

    disable() {
        // Bug: forgot to call this._dbus.unexport()
        this._dbus = null;
    }

    DoSomething() {}
}
