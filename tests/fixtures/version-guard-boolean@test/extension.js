import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Clutter from 'gi://Clutter';
import Meta from 'gi://Meta';

// Boolean feature flag for version detection
const shellVersion46 = !Clutter.Container;

export default class BooleanGuardExtension extends Extension {
    enable() {
        // Compositor guard: use new API when available, fallback otherwise
        if (global.compositor) global.compositor.get_laters().removeLater(this._laterId);
        else Meta.later_remove(this._laterId);

        // Feature detection: check before using deprecated API
        if (Meta.disable_unredirect_for_display)
            Meta.disable_unredirect_for_display(global.display);
    }
    disable() {}
}
