import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class MissingDisableExtension extends Extension {
    enable() {
        this._active = true;
    }
    // Missing cleanup method
}
