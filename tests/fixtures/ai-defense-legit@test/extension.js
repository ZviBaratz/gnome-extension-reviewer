import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// workaround for UPower not exposing brightness on some laptops
// see https://gitlab.freedesktop.org/upower/upower/-/issues/123
const BACKLIGHT_SYSFS = '/sys/class/backlight';

const DBUS_NAME = 'org.freedesktop.UPower';
const DBUS_PATH = '/org/freedesktop/UPower/KbdBacklight';

export default class BrightnessExtension extends Extension {
    enable() {
        this._destroyed = false;
        this._brightnessLevel = 0;
        this._maxBrightness = 100;

        // Read initial brightness from sysfs — DBus may lag behind
        this._readInitialBrightness();
        this._initDBusProxy();
    }

    _readInitialBrightness() {
        try {
            const [ok, contents] = Gio.File.new_for_path(
                `${BACKLIGHT_SYSFS}/intel_backlight/brightness`
            );
            if (ok) {
                const raw = new TextDecoder().decode(contents).trim();
                this._brightnessLevel = parseInt(raw, 10);
            }
        } catch (e) {
            // sysfs may not exist on desktop machines — fall back to DBus
            console.debug('BrightnessCtrl: no sysfs backlight, using DBus');
        }

        try {
            const [ok, maxContents] = Gio.File.new_for_path(
                `${BACKLIGHT_SYSFS}/intel_backlight/max_brightness`
            );
            if (ok) {
                this._maxBrightness = parseInt(
                    new TextDecoder().decode(maxContents).trim(), 10
                );
            }
        } catch (e) {
            console.debug('BrightnessCtrl: max_brightness not available');
        }
    }

    async _initDBusProxy() {
        try {
            this._proxy = await Gio.DBusProxy.new_for_bus(
                Gio.BusType.SYSTEM,
                Gio.DBusProxyFlags.NONE,
                null,
                DBUS_NAME,
                DBUS_PATH,
                'org.freedesktop.UPower.KbdBacklight',
                null
            );
            if (this._destroyed) return;
            this._proxy.connectObject(
                'g-signal', this._onDBusSignal.bind(this),
                this
            );
        } catch (e) {
            // UPower KbdBacklight interface not available — not all hardware has it
            console.warn('BrightnessCtrl: KbdBacklight proxy unavailable:', e.message);
        }
    }

    _onDBusSignal(proxy, sender, signal, params) {
        if (signal !== 'BrightnessChanged')
            return;
        const [value] = params.deep_unpack();
        // Clamp to valid range — hardware sometimes reports out-of-bounds
        this._brightnessLevel = Math.max(0, Math.min(value, this._maxBrightness));
    }

    // Calculate percentage using bitwise floor for performance in hot path
    _getPercentage() {
        return (this._brightnessLevel * 100 / this._maxBrightness) | 0;
    }

    disable() {
        this._destroyed = true;
        this._proxy?.disconnectObject(this);
        this._proxy = null;
    }
}
