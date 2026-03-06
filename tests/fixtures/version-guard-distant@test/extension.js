import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Meta from 'gi://Meta';
import * as Config from 'resource:///org/gnome/shell/misc/config.js';

let unredirectEnabled = true;

export default class DistantGuardExtension extends Extension {
    enable() {
        this._setDisplayUnredirect(true);
    }

    _setDisplayUnredirect(enable) {
        let v48 = Config.PACKAGE_VERSION >= '48';

        if (enable && !unredirectEnabled)
            v48
                ? global.compositor.enable_unredirect()
                : Meta.enable_unredirect_for_display(global.display);
        else if (!enable && unredirectEnabled)
            v48
                ? global.compositor.disable_unredirect()
                : Meta.disable_unredirect_for_display(global.display);

        unredirectEnabled = enable;
    }

    disable() {
        this._setDisplayUnredirect(false);
    }
}
