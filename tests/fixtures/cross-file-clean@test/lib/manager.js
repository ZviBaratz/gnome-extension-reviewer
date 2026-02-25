import GLib from 'gi://GLib';
import {Controller} from './controller.js';

export class Manager {
    enable() {
        this._controller = new Controller();
        this._controller.enable();
        this._handlerId = global.display.connect('window-created', () => {});
    }

    destroy() {
        this._controller.destroy();
        this._controller = null;
        global.display.disconnect(this._handlerId);
        this._handlerId = null;
    }
}
