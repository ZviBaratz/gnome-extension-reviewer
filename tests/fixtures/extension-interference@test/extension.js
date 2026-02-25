import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class InterferenceExt extends Extension {
    enable() {
        const ext = Main.extensionManager.lookup('other@ext');
    }
    disable() {}
}
