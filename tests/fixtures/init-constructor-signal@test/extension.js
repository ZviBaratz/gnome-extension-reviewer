import GObject from 'gi://GObject';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class SignalCallbackExtension extends Extension {
    constructor(metadata) {
        super(metadata);

        // VIOLATION: Shell global accessed directly in constructor
        this._hasOverview = Main.sessionMode.hasOverview;

        // OK: Shell global inside signal callback — deferred, not executed
        // during construction
        this._signalId = this.connect('notify', () => {
            const monitors = Main.layoutManager.monitors;
            Main.panel.addToStatusArea('test', null);
        });

        // OK: multi-line connectObject callback
        this.connectObject('notify::visible', () => {
            if (Main.overview.visible) {
                Main.messageTray.close();
            }
        }, this);
    }

    enable() {
        Main.panel.addToStatusArea('test', this);
    }

    disable() {
        this.disconnect(this._signalId);
    }
}
