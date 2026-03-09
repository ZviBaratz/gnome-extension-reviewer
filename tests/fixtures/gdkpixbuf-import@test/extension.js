import GdkPixbuf from 'gi://GdkPixbuf';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        const pixbuf = GdkPixbuf.Pixbuf.new_from_file('/tmp/icon.png');
    }

    disable() {}
}
