import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class SlopSpreadCopyTest extends Extension {
    enable() {
        const config = { ...this._settings };
        this._apply(config);
    }
    disable() {}
}
