import GLib from 'gi://GLib';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class LifecycleImbalanceExtension extends Extension {
    enable() {
        this._id1 = this._settings.connect('changed::key1', () => {});
        this._id2 = this._settings.connect('changed::key2', () => {});
        this._id3 = this._settings.connect('changed::key3', () => {});
        this._id4 = Main.overview.connect('showing', () => {});
        // Missing: no disconnect calls
        // Untracked timeout: return value not stored
        GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, () => GLib.SOURCE_REMOVE);
    }

    disable() {
        // Only disconnect one of four
        this._settings.disconnect(this._id1);
    }
}
