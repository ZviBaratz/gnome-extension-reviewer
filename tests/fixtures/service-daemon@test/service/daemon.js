import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

// Service daemon: runs in separate GJS process, not in GNOME Shell.
// init/shell-modification should NOT fire here.
const settings = new Gio.Settings({schema_id: 'org.example.myext'});
const variant = new GLib.Variant('s', 'hello');

// R-SLOP-24 should NOT fire for new Gio.Settings() in service/
const userSettings = new Gio.Settings({schema_id: 'org.example.user'});

// constructor-resources should NOT fire for service daemon classes
class DaemonService extends GObject.Object {
    constructor() {
        super();
        this._id = settings.connect('changed', () => {});
    }
}
