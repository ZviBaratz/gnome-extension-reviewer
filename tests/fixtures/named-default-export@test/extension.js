import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// TypeScript and bundlers often emit this form instead of `export default class`
class MyExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
    }

    disable() {
        this._settings = null;
    }
}

export { MyExtension as default };
