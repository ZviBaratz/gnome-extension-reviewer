import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class RunDisposeExtension extends Extension {
    enable() {
        this._widget = {};
    }

    disable() {
        this._widget.run_dispose();
        this._widget = null;
    }
}
