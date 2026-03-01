import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

function processCurrentBatteryThresholdValue(currentBatteryThresholdValue) {
    return currentBatteryThresholdValue > 80;
}

export default class LongParamExtension extends Extension {
    enable() {
        this._result = processCurrentBatteryThresholdValue(85);
    }

    disable() {
        this._result = null;
    }
}
