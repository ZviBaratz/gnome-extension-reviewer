import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class FreezeExtension extends Extension {
    enable() {
        // Should fire R-SLOP-35 (inline object literal)
        this._config = Object.freeze({
            MAX_RETRIES: 3,
            TIMEOUT: 5000,
        });

        // Should NOT fire R-SLOP-35 (freezing existing variable)
        const monitors = this._getMonitors();
        Object.freeze(monitors);
    }

    disable() {
        this._config = null;
    }
}
