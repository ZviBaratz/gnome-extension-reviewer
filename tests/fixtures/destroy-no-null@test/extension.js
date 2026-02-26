import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import St from 'gi://St';

export default class TestExtension extends Extension {
    enable() {
        this._widget = new St.Label({text: 'test'});
        this._button = new St.Button({label: 'test'});
    }

    disable() {
        // BAD: destroy without null
        this._widget.destroy();

        // GOOD: destroy then null
        this._button.destroy();
        this._button = null;
    }
}
