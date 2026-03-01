import GObject from 'gi://GObject';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const MyWidget = GObject.registerClass(
class MyWidget extends GObject.Object {
    destroy() {}
});

export default class EmptyDestroyExtension extends Extension {
    enable() {
        this._widget = new MyWidget();
    }

    disable() {
        this._widget.destroy();
        this._widget = null;
    }
}
