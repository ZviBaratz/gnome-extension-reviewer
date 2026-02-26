import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class SubprocessExtension extends Extension {
    enable() {
        this._proc = new Gio.Subprocess({
            argv: ['/usr/bin/tail', '-f', '/var/log/syslog'],
            flags: Gio.SubprocessFlags.STDOUT_PIPE,
        });
        this._proc.init(null);
    }

    disable() {
        // Bug: no force_exit() or cancel — subprocess keeps running
        this._proc = null;
    }
}
