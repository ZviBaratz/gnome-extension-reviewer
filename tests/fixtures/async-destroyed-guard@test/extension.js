import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class AsyncDestroyedGuardExtension extends Extension {
    enable() {
        this._destroyed = false;
        this._loadDataAsync();
    }

    async _loadDataAsync() {
        const file = Gio.File.new_for_path('/tmp/data.txt');
        const [contents] = await file.load_contents_async(null);
        if (this._destroyed)
            return;
        this._data = contents;
    }

    disable() {
        this._destroyed = true;
        this._data = null;
    }
}
