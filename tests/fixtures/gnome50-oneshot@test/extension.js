import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class OneShotExtension extends Extension {
    enable() {
        // Advisory: one-shot timeout cannot be cancelled
        GLib.timeout_add_once(GLib.PRIORITY_DEFAULT, 500, () => {
            this._applyUpdate();
        });
    }

    _applyUpdate() {}

    disable() {}
}
