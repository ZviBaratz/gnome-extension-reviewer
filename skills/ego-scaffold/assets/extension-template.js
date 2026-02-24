import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class ${CLASS_NAME}Extension extends Extension {
    enable() {
        console.debug(`[${UUID}] Extension enabled`);
        this._settings = this.getSettings();

        // TODO: Add your extension functionality here
        // Create UI elements, connect signals, set up monitors, etc.
        // All resource allocation should happen in enable(), not constructor()
    }

    disable() {
        console.debug(`[${UUID}] Extension disabled`);

        // TODO: Clean up everything created in enable()
        // Disconnect signals, remove timeouts, destroy UI, null references
        // Clean up in reverse order of creation

        this._settings = null;
    }
}
