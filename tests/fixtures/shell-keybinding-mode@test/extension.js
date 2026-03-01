import Shell from 'gi://Shell';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class KeyBindingExtension extends Extension {
    enable() {
        Main.wm.addKeybinding('my-key', this.getSettings(),
            0, Shell.KeyBindingMode.NORMAL, () => {});
    }

    disable() {
        Main.wm.removeKeybinding('my-key');
    }
}
