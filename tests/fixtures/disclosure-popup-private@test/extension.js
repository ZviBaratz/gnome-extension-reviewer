import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class PopupPrivateExtension extends Extension {
    enable() {
        const items = this._menu._getMenuItems();
        this._count = items.length;
    }

    disable() {
        this._count = null;
    }
}
