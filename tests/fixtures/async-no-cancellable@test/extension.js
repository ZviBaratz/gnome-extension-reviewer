import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class AsyncNoCancellableExtension extends Extension {
    enable() {
        this._loadData();
    }

    async _loadData() {
        const file = Gio.File.new_for_path('/some/path');
        const [contents] = await file.load_contents_async(null);
        this._data = new TextDecoder().decode(contents);
    }

    disable() {
        this._data = null;
    }
}
