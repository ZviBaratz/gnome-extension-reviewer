import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class LifecycleCleanExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._settings.connectObject(
            'changed::key1', () => this._onChanged(),
            this
        );
        this._timeoutId = GLib.timeout_add_seconds(
            GLib.PRIORITY_DEFAULT, 5, () => GLib.SOURCE_REMOVE
        );
    }

    _onChanged() {}

    disable() {
        if (this._timeoutId) {
            GLib.Source.remove(this._timeoutId);
            this._timeoutId = null;
        }
        this._settings.disconnectObject(this);
        this._settings = null;
    }
}
