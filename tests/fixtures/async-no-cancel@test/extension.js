import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        this._loadData();
    }

    async _loadData() {
        // Uses Gio async but no Gio.Cancellable
        const file = Gio.File.new_for_path('/tmp/test');
        const [ok, contents] = await file.load_contents_async(null);
    }

    disable() {
        // Missing cancel()/abort() despite async usage
    }
}
