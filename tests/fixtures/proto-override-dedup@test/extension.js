import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {API} from './lib/api.js';

export default class TestExtension extends Extension {
    enable() {
        this._api = new API();
        this._api.open();
    }

    disable() {
        this._api.close();
        this._api = null;
    }
}
