import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class WidgetLeakExtension extends Extension {
    enable() {
        this._label = new St.Label({text: 'Hello'});
        this._button = new St.Button({label: 'Click'});
    }
    disable() {
        // Forgot to destroy widgets!
        this._label = null;
        // _button not even nulled
    }
}
