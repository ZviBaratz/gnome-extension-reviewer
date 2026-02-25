import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class AiSlopRethrowExtension extends Extension {
    enable() {
        try {
            this._settings = this.getSettings();
        } catch(e) { console.error('Failed:', e); throw e; }
    }

    disable() {
        this._settings = null;
    }
}
