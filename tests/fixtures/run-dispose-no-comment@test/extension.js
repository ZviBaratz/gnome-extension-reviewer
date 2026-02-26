import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        this._widget = new Object();
    }

    disable() {
        this._widget.run_dispose();
        this._widget = null;
    }
}
