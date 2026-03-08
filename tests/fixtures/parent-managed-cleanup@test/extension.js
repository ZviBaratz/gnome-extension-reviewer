import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {SignalHelper} from './helper.js';

export default class TestExtension extends Extension {
    enable() {
        this._signals = new SignalHelper();
        this._signals.connect_all();
    }

    disable() {
        this._signals.disconnect_all();
        this._signals = null;
    }
}
