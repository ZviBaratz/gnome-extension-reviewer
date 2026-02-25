import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class AiSlopCleanupExtension extends Extension {
    enable() {
        this._a = {};
        this._b = {};
        this._c = {};
        this._d = {};
        this._e = {};
    }

    disable() {
        if (this._a) { this._a.destroy(); this._a = null; }
        if (this._b) { this._b.destroy(); this._b = null; }
        if (this._c) { this._c.destroy(); this._c = null; }
        if (this._d) { this._d.destroy(); this._d = null; }
        if (this._e) { this._e.destroy(); this._e = null; }
    }
}
