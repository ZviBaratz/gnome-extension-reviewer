import GObject from 'gi://GObject';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const MyWidget = GObject.registerClass(
    class MyWidget extends GObject.Object {
        _init(params) {
            if (typeof super._init === 'function') super._init(params);
        }
    }
);

export default class TestExtension extends Extension {
    enable() {
        this._widget = new MyWidget();
    }

    disable() {
        this._widget = null;
    }
}
