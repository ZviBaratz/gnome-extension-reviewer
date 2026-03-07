import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

// Module-scope prototype mutation — should trigger R-LIFE-27
PanelMenu.Button.prototype.customMethod = function() {
    return true;
};

// Module-scope Object.assign — should also trigger
Object.assign(PanelMenu.Button.prototype, {
    anotherMethod() { return false; }
});

export default class TestExtension extends Extension {
    enable() {
        // Inside enable() — should NOT trigger R-LIFE-27
        PanelMenu.Button.prototype.enableMethod = function() {};
    }

    disable() {
        delete PanelMenu.Button.prototype.enableMethod;
    }
}
