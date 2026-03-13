import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        this._doWork().catch(e => console.error(e));
        this._fetchData().catch(e => console.error(e));
        this._loadData().catch(e => console.error(e));
    }

    _doWork() {
        return 42;
    }

    async _fetchData() {
        return Promise.resolve('ok');
    }

    _loadData() {
        return new Promise((resolve, reject) => {
            resolve('loaded');
        });
    }

    disable() {}
}
