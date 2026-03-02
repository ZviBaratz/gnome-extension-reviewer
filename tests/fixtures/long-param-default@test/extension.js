import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    // Parameter with default — should NOT trigger R-SLOP-38
    _removeWidget(widget_not_already_destroyed = true) {
        if (widget_not_already_destroyed) {
            this._widget?.destroy();
        }
    }

    enable() {}
    disable() {}
}
