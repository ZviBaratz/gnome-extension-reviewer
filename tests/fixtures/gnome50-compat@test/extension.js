import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as KeyboardManager from 'resource:///org/gnome/shell/misc/keyboardManager.js';

export default class Gnome50CompatTest extends Extension {
    enable() {
        KeyboardManager.holdKeyboard();

        this._restartId = global.display.connect('show-restart-message', () => {
            console.log('restart message');
        });

        this._restartSigId = global.display.connect('restart', () => {
            console.log('restarting');
        });
    }

    disable() {
        KeyboardManager.releaseKeyboard();

        if (this._restartId) {
            global.display.disconnect(this._restartId);
            this._restartId = null;
        }

        if (this._restartSigId) {
            global.display.disconnect(this._restartSigId);
            this._restartSigId = null;
        }
    }
}
