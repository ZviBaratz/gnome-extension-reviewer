import GLib from 'gi://GLib';
import {Controller} from './controller.js';

export class Manager {
    enable() {
        this._controller = new Controller();
        this._controller.enable();
        // This signal is never disconnected — INTENTIONAL LEAK
        this._handlerId = global.display.connect('window-created', () => {});
    }

    destroy() {
        this._controller.destroy();
        this._controller = null;
        // Missing: global.display.disconnect(this._handlerId);
    }
}
