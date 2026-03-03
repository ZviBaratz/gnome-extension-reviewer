import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Meta from 'gi://Meta';
import * as Config from 'resource:///org/gnome/shell/misc/config.js';

export default class PkgVerGuardExtension extends Extension {
    enable() {
        // PACKAGE_VERSION guard for deprecated Meta display functions
        let v48 = Config.PACKAGE_VERSION >= '48'
        v48
            ? global.compositor.enable_unredirect()
            : Meta.enable_unredirect_for_display(global.display)
    }

    disable() {}
}
