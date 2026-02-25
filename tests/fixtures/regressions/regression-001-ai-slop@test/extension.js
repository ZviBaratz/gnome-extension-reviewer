import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

/**
 * Initialize the power manager
 * @param {Gio.Settings} settings - The extension settings
 * @returns {boolean} Whether initialization was successful
 */
function initPowerManager(settings) {
    return true;
}

// Important: Make sure to initialize settings before use
// Note: Ensure proper cleanup in disable method

export default class RegressionExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        try {
            this._proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SYSTEM, 0, null,
                'org.freedesktop.UPower', '/org/freedesktop/UPower',
                'org.freedesktop.UPower', null);
        } catch(e) { console.error(`Failed to create proxy: ${e.message}`); throw e; }
    }

    disable() {
        if (this._settings) { this._settings.destroy(); this._settings = null; }
        if (this._proxy) { this._proxy.destroy(); this._proxy = null; }
    }
}
