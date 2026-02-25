import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {Manager} from './lib/manager.js';

export default class CrossFileLeakExtension extends Extension {
    enable() {
        this._manager = new Manager();
        this._manager.enable();
    }

    disable() {
        this._manager.destroy();
        this._manager = null;
    }
}
