import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        this._device = this._getDevice();
        if (this._device && typeof this._device.getBatteryLevel === 'function')
            this._level = this._device.getBatteryLevel();
    }

    _getDevice() {
        return null;
    }

    disable() {
        this._device = null;
    }
}
