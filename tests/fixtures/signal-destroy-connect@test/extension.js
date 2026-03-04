import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class DestroySignalExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._settingsId = this._settings.connect('changed::key', () => {});

        // 'destroy' signal — self-cleaning, no disconnect needed
        this._button = new St.Button();
        this._button.connect('destroy', () => {
            this._button = null;
        });

        // Another destroy signal on a different widget
        this._icon = new St.Icon();
        this._icon.connect('destroy', () => {
            this._icon = null;
        });
    }

    disable() {
        this._settings.disconnect(this._settingsId);
        this._settings = null;
        this._button?.destroy();
        this._icon?.destroy();
    }
}
