import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {StatusNotifierItem} from './statusNotifierItem.js';

export default class SmartCleanupExtension extends Extension {
    enable() {
        this._item = new StatusNotifierItem(this.getSettings());
    }

    disable() {
        this._item.disconnectSmart();
        this._item = null;
    }
}
