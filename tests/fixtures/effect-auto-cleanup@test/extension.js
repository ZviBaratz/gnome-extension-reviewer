import GLib from 'gi://GLib';
import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {BlurEffect} from './effect.js';

export default class TestExtension extends Extension {
    enable() {
        this._overlay = new St.Widget();
        this._effect = new BlurEffect();
        this._overlay.add_effect(this._effect);
    }

    disable() {
        // Destroying the overlay auto-destroys its effects
        this._overlay.destroy();
        this._overlay = null;
    }
}
