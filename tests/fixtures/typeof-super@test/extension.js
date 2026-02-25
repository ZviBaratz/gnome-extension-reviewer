import GObject from 'gi://GObject';
import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const MyWidget = GObject.registerClass(
class MyWidget extends St.BoxLayout {
    _init() {
        if (typeof super._init === 'function')
            super._init();
    }
    destroy() {
        if (typeof super.destroy === 'function')
            super.destroy();
    }
});

export default class TestExtension extends Extension {
    enable() { this._w = new MyWidget(); }
    disable() { this._w.destroy(); this._w = null; }
}
