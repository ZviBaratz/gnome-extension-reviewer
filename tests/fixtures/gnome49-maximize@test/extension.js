import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class Gnome49MaximizeTest extends Extension {
    enable() {
        const win = global.display.focus_window;
        win.maximize(Meta.MaximizeFlags.BOTH);
    }
    disable() {}
}
