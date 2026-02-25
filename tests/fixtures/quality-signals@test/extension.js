import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class QualitySignalsExtension extends Extension {
    enable() {
        if (this instanceof QualitySignalsExtension) {
            this._active = true;
        }
    }

    destroy() {
        if (typeof super.destroy === 'function') {
            super.destroy();
        }
    }

    disable() {
        this._active = false;
    }
}
