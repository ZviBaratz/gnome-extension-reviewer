import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

/**
 * @param {string} name - The name parameter
 * @returns {boolean} Whether it worked
 */
function helperFunction(name) {
    return true;
}

export default class AiSlopExtension extends Extension {
    enable() {
        this._initializing = false;
        this._pendingDestroy = false;
        this._indicator = null;

        if (!Main.sessionMode.isLocked && this._indicator === null)
            this._initAsync();
    }

    async _initAsync() {
        if (this._initializing) return;
        this._initializing = true;
        try {
            this._indicator = {};
            if (this._pendingDestroy) return;
        } finally {
            this._initializing = false;
            if (this._pendingDestroy) {
                this._pendingDestroy = false;
                this._cleanup();
            }
        }
    }

    _cleanup() {
        if (this._initializing) {
            this._pendingDestroy = true;
            return;
        }
        if (this._indicator) {
            try {
                this._indicator.destroy();
            } catch (e) {
                console.error(`Error: ${e}`);
            }
            this._indicator = null;
        }
    }

    disable() {
        this._cleanup();
    }
}
