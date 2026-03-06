import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import St from 'gi://St';
import * as Util from './util.js';

export default class TestExtension extends Extension {
    enable() {
        this._actors = [new St.Label(), new St.Button()];
        this._widget = new St.Label({text: 'test'});
    }

    disable() {
        // BAD: .destroy without () — property access, not method call
        this._actors.forEach((actor) => actor.destroy);

        // GOOD: .destroy() with parens
        this._widget.destroy();
        this._widget = null;

        // GOOD: callback reference in connectSmart (FP suppression)
        Util.connectSmart(this._widget, 'destroy', this, this.destroy);

        // GOOD: existence check (FP suppression)
        if (this._widget.destroy) {
            this._widget.destroy();
        }

        // GOOD: typeof check (FP suppression)
        if (typeof this._widget.destroy === 'function') {
            this._widget.destroy();
        }
    }
}
