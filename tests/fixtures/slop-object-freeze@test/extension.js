import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const CONFIG = Object.freeze({
    MAX_RETRIES: 3,
    TIMEOUT: 5000,
});

export default class FreezeExtension extends Extension {
    enable() {
        this._config = CONFIG;
    }

    disable() {
        this._config = null;
    }
}
