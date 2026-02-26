import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import St from 'gi://St';

export default class TestExtension extends Extension {
    enable() {
        this._clipboard = St.Clipboard.get_default();
        Main.wm.addKeybinding('copy-text', this.getSettings(),
            0, 0, () => this._onCopy());
    }

    _onCopy() {
        this._clipboard.set_text(0, 'test');
    }

    disable() {
        Main.wm.removeKeybinding('copy-text');
        this._clipboard = null;
    }
}
