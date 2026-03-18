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

// R-DEPR-06 should NOT fire for Tweener in service/
const Tweener = imports.tweener.tweener;

// R-DEPR-10 should NOT fire for imports.format in service/
let fmt = imports.format;

// constructor-resources should NOT fire for service daemon classes
class DaemonService extends GObject.Object {
    constructor() {
        super();
        this._id = settings.connect('changed', () => {});
    }
}

// R-LOG-02 should NOT fire for log() in service/
log('daemon started');

// R-LOG-03 should NOT fire for print() in service/
print('daemon output');

// R-SLOP-43 should NOT fire for underscore exports in service/
export function _internalHelper() {}

// R-QUAL-32 should NOT fire for version specifiers in service/
import GLib2 from 'gi://GLib?version=2.0';

// R-QUAL-34 should NOT fire for sync enumerate in service/
const iter = dir.enumerate_children('standard::*', Gio.FileQueryInfoFlags.NONE, null);

// R-QUAL-35 should NOT fire for sync D-Bus in service/
const reply = proxy.call_sync('Method', null, 0, -1, null);

// quality/module-state should NOT fire for module vars in service/
let daemonState = null;

// lifecycle/untracked-timeout should NOT fire in service/
GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, () => {
    return GLib.SOURCE_REMOVE;
});
