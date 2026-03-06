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

        // BAD: .destroy in if-body, not condition (should still flag)
        if (this._shouldCleanup) this._widget.destroy;

        // GOOD: .destroy() with parens
        this._widget.destroy();

        // GOOD: optional chaining call (FP suppression)
        this._widget.destroy?.();
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

        // GOOD: bound method reference (FP suppression)
        const cleanup = this._widget.destroy.bind(this._widget);

        // GOOD: .call/.apply invocation (FP suppression)
        St.Widget.prototype.destroy.call(this._widget);
        St.Widget.prototype.destroy.apply(this._widget, []);

        // GOOD: property assignment (FP suppression)
        this._widget.destroy = null;

        // GOOD: ternary existence check (FP suppression)
        this._widget.destroy ? this._widget.destroy() : null;

        // GOOD: destructuring (FP suppression)
        const {destroy} = this._widget;
    }
}
