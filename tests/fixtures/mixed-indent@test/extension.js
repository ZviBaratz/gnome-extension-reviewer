import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class MixedExt extends Extension {
    enable() {
        this._a = 1;
        this._b = 2;
        this._c = 3;
        this._d = 4;
        this._e = 5;
        this._f = 6;
        this._g = 7;
	enable2() {
		this._h = 8;
		this._i = 9;
		this._j = 10;
		this._k = 11;
		this._l = 12;
		this._m = 13;
		this._n = 14;
	}
    }
    disable() {
        this._a = null;
    }
}
