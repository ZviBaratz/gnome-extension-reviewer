import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

export default class SecurityExtension extends Extension {
    enable() {
        eval('console.debug("bad")');
        const fn = new Function('return 1');
        const url = 'http://example.com/api';
        const proc = Gio.Subprocess.new(['/bin/sh', '-c', 'echo hello'], 0);
    }

    disable() {}
}
