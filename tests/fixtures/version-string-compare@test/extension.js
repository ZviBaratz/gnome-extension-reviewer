import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Config from 'resource:///org/gnome/shell/misc/config.js';

export default class VersionCompareExtension extends Extension {
    enable() {
        // Bug: string comparison on version is unreliable
        if (Config.PACKAGE_VERSION >= '45') {
            this._useNewAPI = true;
        }
    }

    disable() {
        this._useNewAPI = null;
    }
}
