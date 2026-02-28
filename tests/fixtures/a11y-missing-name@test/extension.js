import St from 'gi://St';
import GObject from 'gi://GObject';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

class CustomWidget extends St.Widget {
    _init() {
        super._init();
    }
}

GObject.registerClass(CustomWidget);

export default class A11yTest extends Extension {
    enable() {
        this._button = new St.Button({
            icon_name: 'system-settings-symbolic',
            style_class: 'panel-button',
        });
    }
    disable() {
        this._button?.destroy();
        this._button = null;
    }
}
