import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        this._timeoutId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 5, () => {
            return GLib.SOURCE_CONTINUE;
        });
    }

    disable() {
        // BUG: stores timeout ID but never calls GLib.Source.remove()
        this._timeoutId = null;
    }
}
