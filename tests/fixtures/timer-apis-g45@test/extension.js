import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class WebApisGnome45Extension extends Extension {
    enable() {
        this._timer = setTimeout(() => {}, 100);
        this._interval = setInterval(() => {}, 1000);
    }

    disable() {
        clearTimeout(this._timer);
        clearInterval(this._interval);
    }
}
