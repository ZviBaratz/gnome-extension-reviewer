import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Shell from 'gi://Shell';
import Meta from 'gi://Meta';

export default class KeybindingExt extends Extension {
    enable() {
        Main.wm.addKeybinding(
            'my-shortcut',
            this.getSettings(),
            Meta.KeyBindingFlags.IGNORE_AUTOREPEAT,
            Shell.ActionMode.NORMAL,
            () => { this._onShortcut(); }
        );
    }
    _onShortcut() {}
    disable() {
        // BUG: missing removeKeybinding
    }
}
