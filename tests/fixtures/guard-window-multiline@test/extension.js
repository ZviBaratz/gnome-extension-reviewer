import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Meta from 'gi://Meta';

export default class GuardWindowExtension extends Extension {
    enable() {
        // Version-compat: use compositor API when available
        if (global.compositor) {
            global.compositor.get_laters().removeLater(this._laterId);
        } else {
            // Fallback for older GNOME
            // (6 lines after the guard)
            Meta.later_remove(this._laterId);
        }
    }
    disable() {}
}
