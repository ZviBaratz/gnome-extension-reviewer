import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

export default class NonExecutableScriptTest extends Extension {
    enable() {
        // Uses pkexec to justify having a helper script
        const proc = new Gio.Subprocess({
            argv: ['pkexec', '/usr/local/bin/helper'],
        });
    }
    disable() {}
}
