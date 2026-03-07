import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Meta from 'gi://Meta';
import Gio from 'gi://Gio';

let GioUnix;
try {
    GioUnix = (await import('gi://GioUnix')).default;
} catch {
    // fallback for GNOME < 46
}

export default class VersionReplacementCompat extends Extension {
    enable() {
        // R-VER44-02: old API (suppressed — file contains "get_laters")
        Meta.later_remove(this._laterId);

        // R-VER46-04: old API (suppressed — file contains "GioUnix")
        this._stream = new Gio.UnixInputStream({fd: 0});

        // R-VER49-08: old API (suppressed — file contains "set_maximize_flags")
        this._win.maximize(Meta.MaximizeFlags.BOTH);

        // R-VER49-11: old API (suppressed — file contains "set_maximize_flags")
        this._win.unmaximize(Meta.MaximizeFlags.BOTH);
    }

    _newApi() {
        // Replacement APIs present in file for version-compat
        const laters = global.compositor.get_laters();
        laters.removeLater(this._laterId);
        this._win.set_maximize_flags(Meta.MaximizeFlags.BOTH);
        this._win.maximize();
    }

    disable() {
        this._stream = null;
        this._win = null;
    }
}
