import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Clutter from 'gi://Clutter';
import Cogl from 'gi://Cogl';
import {shellVersionIsAtLeast} from 'resource:///org/gnome/shell/misc/util.js';

// Cross-version color API: the canonical migration pattern for GNOME 47
// Clutter.Color in the else-branch is valid — it only runs on GNOME < 47
export function parseColor(string) {
    let color;
    if (shellVersionIsAtLeast(47, 'alpha')) {
        color = Cogl.Color.from_string(string)[1];
    } else {
        color = Clutter.Color.from_string(string)[1];
    }
    return color;
}

export default class VersionGuard47Extension extends Extension {
    enable() {
        this._color = parseColor('#ff0000');
    }

    disable() {
        this._color = null;
    }
}
