import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class DestroyedDensityExtension extends Extension {
    enable() {
        this._destroyed = false;
        if (this._destroyed) return;
        this._initA();
        if (this._destroyed) return;
        this._initB();
        if (this._destroyed) return;
        this._initC();
        if (this._destroyed) return;
        this._initD();
        if (this._destroyed) return;
        this._initE();
        if (this._destroyed) return;
        this._initF();
        if (this._destroyed) return;
        this._initG();
        if (this._destroyed) return;
        this._initH();
        if (this._destroyed) return;
        this._initI();
        if (this._destroyed) return;
        this._initJ();
        if (this._destroyed) return;
    }

    disable() {
        this._destroyed = true;
    }

    _initA() { if (this._destroyed) return; }
    _initB() { if (this._destroyed) return; }
    _initC() { if (this._destroyed) return; }
    _initD() { if (this._destroyed) return; }
    _initE() { if (this._destroyed) return; }
    _initF() { if (this._destroyed) return; }
    _initG() { if (this._destroyed) return; }
    _initH() { if (this._destroyed) return; }
    _initI() { if (this._destroyed) return; }
    _initJ() { if (this._destroyed) return; }
}
