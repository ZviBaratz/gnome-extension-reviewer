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

// Indirect prototype mutation via function call — should trigger R-LIFE-27
function _promisifySignals(proto) {
    proto.connect_once = function(signal) { return signal; };
}
_promisifySignals(GObject.Object.prototype);

// Equality comparison — should NOT trigger any warning
const isOriginal = PanelMenu.Button.prototype.customMethod === originalFn;

// instanceof check — should NOT trigger
if (obj instanceof PanelMenu.Button.prototype.constructor) {}

// Object.getPrototypeOf — should NOT trigger (exercises PROTO_SAFE filter)
const proto = Object.getPrototypeOf(PanelMenu.Button.prototype);

// Object.create — should NOT trigger (exercises PROTO_SAFE filter)
const child = Object.create(PanelMenu.Button.prototype);

// Gio._promisify — should NOT trigger (handled by R-QUAL-33 instead)
Gio._promisify(Gio.File.prototype, 'load_contents_async', 'load_contents_finish');

export default class TestExtension extends Extension {
    enable() {
        // Inside enable() — should NOT trigger R-LIFE-27
        PanelMenu.Button.prototype.enableMethod = function() {};
    }

    disable() {
        delete PanelMenu.Button.prototype.enableMethod;
    }
}
