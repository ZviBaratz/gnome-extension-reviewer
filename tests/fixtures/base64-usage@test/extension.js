import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class Base64Extension extends Extension {
    enable() {
        const encoded = btoa('secret data');
        this._data = atob(encoded);
    }
    disable() {
        this._data = null;
    }
}
