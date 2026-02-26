import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class GSettingsBindFlagsTest extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._settings.bind('my-key', this._widget, 'value', GObject.BindingFlags.DEFAULT);
    }
    disable() {
        this._settings = null;
    }
}
