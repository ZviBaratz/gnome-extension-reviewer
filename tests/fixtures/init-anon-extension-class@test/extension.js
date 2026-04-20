import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

// Helper class — its constructor runs only when instantiated from enable(),
// not at module load time. The anonymous extension class detection must
// correctly identify the Extension class boundary so this constructor
// is NOT flagged as an init-time Shell modification.
class ColorViewer {
    constructor() {
        this._cancellable = new Gio.Cancellable();
        this._session = new Gio.SocketClient();
    }

    destroy() {
        this._cancellable.cancel();
        this._cancellable = null;
        this._session = null;
    }
}

// Anonymous extension class (GNOME 45+ bundle style, e.g. tuberry extensions).
// Uses `export default class extends X.Extension` without a class name.
export default class extends Extension {
    enable() {
        this._viewer = new ColorViewer();
    }

    disable() {
        this._viewer.destroy();
        this._viewer = null;
    }
}
