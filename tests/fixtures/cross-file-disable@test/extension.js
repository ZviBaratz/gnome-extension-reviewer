import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {Manager} from './lib/manager.js';

export default class CrossFileDisableExtension extends Extension {
    enable() {
        this._manager = new Manager();
        this._manager.enable();
    }

    disable() {
        this._manager.disable();
        this._manager = null;
    }
}
