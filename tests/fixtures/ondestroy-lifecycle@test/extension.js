import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import St from 'gi://St';

export default class LifecycleExtension extends Extension {
    enable() {
        this._label = new St.Label({text: 'Hello'});
    }

    _onDestroy() {
        this._label = null;
    }

    disable() {
        if (this._label) {
            this._label.destroy();
        }
    }
}
