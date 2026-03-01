import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class SyncIOExtension extends Extension {
    enable() {
        const dir = Gio.File.new_for_path('/tmp');
        const children = dir.enumerate_children('standard::name', Gio.FileQueryInfoFlags.NONE, null);
        this._files = [];
        let info;
        while ((info = children.next_file(null)) !== null)
            this._files.push(info.get_name());
    }

    disable() {
        this._files = null;
    }
}
