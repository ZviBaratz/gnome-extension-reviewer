import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Meta from 'gi://Meta';
import * as Config from 'resource:///org/gnome/shell/misc/config.js';

export default class ConfigPrefixGuardExtension extends Extension {
    enable() {
        // Config.PACKAGE_VERSION guard — no global.compositor in this file
        // so replacement-pattern won't suppress; guard-pattern must work
        if (Config.PACKAGE_VERSION >= '48') {
            this._useNewAPI();
        } else {
            let actors = Meta.get_window_actors();
            this._processActors(actors);
        }
    }

    disable() {}
}
