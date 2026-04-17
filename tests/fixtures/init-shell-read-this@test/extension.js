import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export default class InitShellReadThisExtension extends Extension {
    constructor(metadata) {
        super(metadata);

        // ADVISORY (WARN): constructor stores Shell global reference via
        // this.x assignment — reads reference, does not mutate Shell state.
        // Pattern: clipboard-indicator, dash-to-panel, hara-hachi-bu.
        this._panel = Main.panel;
    }

    enable() {
        this._panel.addToStatusArea('test', this);
    }

    disable() {
        this._panel = null;
    }
}
