import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

import TestWidget from './widget.js';

export default class TestExtension extends Extension {
    enable() {
        this._widget = new TestWidget();
    }

    disable() {
        this._widget.destroy();
        this._widget = null;
    }
}
