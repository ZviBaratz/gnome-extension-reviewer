import * as Mainloop from 'mainloop';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class DeprecatedModulesExtension extends Extension {
    enable() {
        this._timeoutId = Mainloop.timeout_add(1000, () => {
            return true;
        });
    }

    disable() {
        if (this._timeoutId) {
            Mainloop.source_remove(this._timeoutId);
            this._timeoutId = null;
        }
    }
}
