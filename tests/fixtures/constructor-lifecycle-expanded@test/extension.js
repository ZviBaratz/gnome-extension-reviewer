import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Cogl from 'gi://Cogl';

// OK: Cogl.Color is a value type (no system resources)
const BG_COLOR = new Cogl.Color({red: 0, green: 0, blue: 0, alpha: 0});

// OK: second Cogl.Color constant
const FG_COLOR = new Cogl.Color({red: 255, green: 0, blue: 0, alpha: 255});

export default class LifecycleExpandedExtension extends Extension {
    enable() {
        this._bg = BG_COLOR;
    }
    disable() {
        this._bg = null;
    }
}
