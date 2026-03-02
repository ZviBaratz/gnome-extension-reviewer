import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

let GioUnix;
try {
    GioUnix = (await import('gi://GioUnix')).default;
} catch {
    GioUnix = {
        InputStream: Gio.UnixInputStream,
    };
}

export default class MyExtension extends Extension {
    enable() {
        this._stream = new GioUnix.InputStream({fd: 0});
    }

    disable() {
        this._stream = null;
    }
}
