import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class AsyncExt extends Extension {
    async enable() {
        const data = await this._loadData();
        this._process(data);
    }
    async _loadData() {
        return new Promise(resolve => {
            GLib.timeout_add(GLib.PRIORITY_DEFAULT, 100, () => {
                resolve({});
                return GLib.SOURCE_REMOVE;
            });
        });
    }
    _process(data) {}
    disable() {}
}
