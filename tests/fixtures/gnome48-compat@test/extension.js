import Clutter from 'gi://Clutter';
import Meta from 'gi://Meta';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class Gnome48CompatExtension extends Extension {
    enable() {
        let image = new Clutter.Image();
        Meta.disable_unredirect_for_display(global.display);
    }

    disable() {}
}
