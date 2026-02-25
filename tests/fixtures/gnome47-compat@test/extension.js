import Clutter from 'gi://Clutter';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class Gnome47CompatExtension extends Extension {
    enable() {
        let color = new Clutter.Color({red: 255, green: 0, blue: 0, alpha: 255});
    }

    disable() {}
}
