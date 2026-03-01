import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class SubprocessExtension extends Extension {
    enable() {
        const proc = new Gio.Subprocess({
            argv: ['/usr/bin/brightnessctl', 'get'],
            flags: Gio.SubprocessFlags.STDOUT_PIPE,
        });
        proc.init(null);
    }

    disable() {}
}
