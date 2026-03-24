import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Config from 'resource:///org/gnome/shell/misc/config.js';

const ShellVersion = parseFloat(Config.PACKAGE_VERSION);

export default class VersionGuardExtension extends Extension {
    enable() {
        this._addActor();
    }

    _addActor() {
        // Version-guarded compat code: add_actor() only runs on GNOME < 46
        if (ShellVersion >= 46) {
            this._box.add_child(this._actor);
        } else {
            this._box.add_actor(this._actor);
        }
    }

    _removeActor() {
        // Version-guarded compat code: remove_actor() only runs on GNOME < 46
        if (ShellVersion >= 46) {
            this._box.remove_child(this._actor);
        } else {
            this._box.remove_actor(this._actor);
        }
    }

    disable() {
        this._removeActor();
        this._box = null;
        this._actor = null;
    }
}
