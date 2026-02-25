import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export default class SessionModesTest extends Extension {
    enable() {
        this._settings = this.getSettings();
    }

    disable() {
        if (Main.sessionMode.currentMode === 'unlock-dialog')
            return;
        this._settings = null;
    }
}
