import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// Guarded: callback/function-ref suffix — should NOT trigger R-SLOP-38
function sortWindowsCompareFunction(a, b) {
    return a.x - b.x;
}

export default class TestExtension extends Extension {
    enable() {
        // Guarded: long identifier ending in Id — should NOT trigger
        const taskbarBoxAllocationChangedId = this._box.connect('allocation-changed', () => {});
        this._box.disconnect(taskbarBoxAllocationChangedId);

        // Guarded: callback suffix — should NOT trigger
        this._windows.sort(sortWindowsCompareFunction);

        // Guarded: handler suffix — should NOT trigger
        this._runPanelAnimationHandler(data);

        // NOT guarded: AI-style verbose name — SHOULD trigger R-SLOP-38
        this._process(currentBatteryThresholdValue);
    }

    _runPanelAnimationHandler(data) {
        return data;
    }

    disable() {
        this._box = null;
    }
}
