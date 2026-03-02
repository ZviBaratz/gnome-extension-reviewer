import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

class ContactStore {
    async fetch() {
        // Method definition named fetch — not browser API
        return [];
    }
}

export default class MyExtension extends Extension {
    enable() {
        this._store = new ContactStore();
        this._store.fetch();
    }

    disable() {
        this._store = null;
    }
}
