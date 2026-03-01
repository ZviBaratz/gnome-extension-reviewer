import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class FreezeExtension extends Extension {
    enable() {
        this._config = Object.freeze({
            MAX_RETRIES: 3,
            TIMEOUT: 5000,
        });
    }

    disable() {
        this._config = null;
    }
}
