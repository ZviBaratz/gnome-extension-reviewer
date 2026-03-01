import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

Gio._promisify(Gio.File.prototype, 'load_contents_async', 'load_contents_finish');
Gio._promisify(Gio.Subprocess.prototype, 'communicate_utf8_async', 'communicate_utf8_finish');

export default class PromisifyExtension extends Extension {
    async enable() {
        const file = Gio.File.new_for_path('/tmp/test');
        const [contents] = await file.load_contents_async(null);
        this._data = contents;
    }

    disable() {
        this._data = null;
    }
}
