import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        let [ok, stdout] = GLib.spawn_sync(null, ['ls'], null, 0, null);
    }

    disable() {}
}
