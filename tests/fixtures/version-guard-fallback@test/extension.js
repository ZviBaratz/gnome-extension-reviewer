import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Clutter from 'gi://Clutter';
import Cogl from 'gi://Cogl';

// Version-compat fallback: use ClickGesture if available, fall back to ClickAction
const ClickActionClass = Clutter.ClickGesture || Clutter.ClickAction;

// Ternary guard: use new color API when available, fall back to legacy
const ColorClass = Clutter.Color ? Clutter.Color : Cogl.Color;

export default class FallbackExtension extends Extension {
    enable() {
        this._action = new ClickActionClass();
        this._color = new ColorClass();

        // Feature detection guard: if-check before using deprecated API
        if (Clutter.ClickAction)
            this._legacyAction = new Clutter.ClickAction();
    }
    disable() {
        this._action = null;
        this._color = null;
        this._legacyAction = null;
    }
}
