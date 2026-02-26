import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Meta from 'gi://Meta';

export default class UnmaxExtension extends Extension {
    enable() {
        this._handler = global.display.connect('window-created', (_, win) => {
            win.unmaximize(Meta.MaximizeFlags.BOTH);
        });
    }
    disable() {
        global.display.disconnect(this._handler);
        this._handler = null;
    }
}
