import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// Important: Make sure to always initialize settings before use
// Note: Ensure proper cleanup in disable method
// Remember: Always handle errors gracefully

export default class AiSlopCommentsExtension extends Extension {
    enable() {
        // TODO: Don't forget to add error handling
        this._settings = this.getSettings();
    }

    disable() {
        this._settings = null;
    }
}
