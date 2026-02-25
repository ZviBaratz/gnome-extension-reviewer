import {Extension, InjectionManager} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export default class InjectionLeakExtension extends Extension {
    enable() {
        this._injectionManager = new InjectionManager();
        this._injectionManager.overrideMethod(
            Main.panel.constructor.prototype, '_updatePanel',
            originalMethod => function (...args) {
                return originalMethod.call(this, ...args);
            }
        );
    }

    disable() {
        // BUG: Missing this._injectionManager.clear()
        this._injectionManager = null;
    }
}
