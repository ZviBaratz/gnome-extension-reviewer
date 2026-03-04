import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export default class TestExtension extends Extension {
    enable() {
        if (!this._isLocked()) {
            this._applySettings();
        }
    }

    disable() {
        this._revertSettings();
    }

    _isLocked() {
        return Main.sessionMode.isLocked;
    }

    _applySettings() {}
    _revertSettings() {}
}
