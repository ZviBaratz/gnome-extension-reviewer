import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TimerExtension extends Extension {
    enable() {
        setTimeout(() => {
            this._ready = true;
        }, 1000);
    }

    disable() {
        this._ready = false;
    }
}
