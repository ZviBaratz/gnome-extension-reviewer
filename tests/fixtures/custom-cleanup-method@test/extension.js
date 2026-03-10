import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {SignalTracker} from './tracker.js';

export default class TestExtension extends Extension {
    enable() {
        this._tracker = new SignalTracker();
        this._tracker.track(global.display, 'window-created');
    }

    disable() {
        this._tracker.disconnect_all();
        this._tracker = null;
    }
}
