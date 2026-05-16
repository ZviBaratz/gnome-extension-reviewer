import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// GdkPixbuf aliased as Meta (as in AppIndicator promiseUtils.js)
import GdkPixbuf from 'gi://GdkPixbuf';
const { GLib, Gio, GObject, GdkPixbuf: Meta } = imports.gi;

export default class TestExtension extends Extension {
    enable() {
        // Meta here is GdkPixbuf — R-VER44-01 should NOT fire
        const pixbuf = Meta.new_from_file('icon.png');
        Meta.later_add(1, () => {});
    }

    disable() {}
}
