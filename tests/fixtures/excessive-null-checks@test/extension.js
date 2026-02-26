import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class ExcessiveNullChecksTest extends Extension {
    enable() {
        if (this._a === null) this._a = 1;
        if (this._b !== null) this._b.destroy();
        if (this._c === undefined) this._c = 2;
        if (typeof this._d !== 'undefined') this._d.run();
        if (this._e === null) this._e = 3;
        if (this._f !== null) this._f.destroy();
        if (this._g === undefined) this._g = 4;
        if (typeof this._h !== 'undefined') this._h.run();
        if (this._i === null) this._i = 5;
        if (this._j !== null) this._j.destroy();
        if (this._k === undefined) this._k = 6;
        if (typeof this._l !== 'undefined') this._l.run();
        if (this._m === null) this._m = 7;
        if (this._n !== null) this._n.destroy();
        if (this._o === undefined) this._o = 8;
        if (typeof this._p !== 'undefined') this._p.run();
    }
    disable() {
        if (this._a !== null) this._a = null;
        if (this._b !== null) this._b = null;
        if (this._c !== null) this._c = null;
        if (this._d !== null) this._d = null;
    }
}
