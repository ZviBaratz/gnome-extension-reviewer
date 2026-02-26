import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TimeoutReassignExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._settings.connect('changed::interval', () => this._scheduleUpdate());
        this._settings.connect('changed::mode', () => this._scheduleRefresh());
    }

    _scheduleUpdate() {
        // Bug: reassigns timeout ID without removing previous source
        this._timerId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 300, () => {
            this._applySettings();
            return GLib.SOURCE_REMOVE;
        });
    }

    _scheduleRefresh() {
        // Same bug: second assignment site also reassigns without removal
        this._timerId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 500, () => {
            this._refreshUI();
            return GLib.SOURCE_REMOVE;
        });
    }

    _applySettings() {}
    _refreshUI() {}

    disable() {
        if (this._timerId) {
            GLib.Source.remove(this._timerId);
            this._timerId = null;
        }
    }
}
