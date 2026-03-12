import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {ParentA} from './parent_a.js';
import {ParentB} from './parent_b.js';

export default class TestExtension extends Extension {
    enable() {
        this._a = new ParentA();
        this._b = new ParentB();
    }

    disable() {
        this._a.disable();
        this._b.disable();
        this._a = null;
        this._b = null;
    }
}
