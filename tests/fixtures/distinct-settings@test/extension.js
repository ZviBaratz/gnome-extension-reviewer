import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class DistinctSettingsExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._desktopSettings = this.getSettings('org.freedesktop.desktop.interface');
        this._a11ySettings = this.getSettings('org.freedesktop.desktop.a11y');
        this._wmSettings = this.getSettings('org.freedesktop.desktop.wm.preferences');
    }

    disable() {
        this._settings = null;
        this._desktopSettings = null;
        this._a11ySettings = null;
        this._wmSettings = null;
    }
}
