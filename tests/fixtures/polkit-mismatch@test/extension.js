import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class PolkitMismatchTest extends Extension {
    enable() {
        const proc = Gio.Subprocess.new(
            ['pkexec', '/usr/local/bin/helper.sh'],
            Gio.SubprocessFlags.NONE
        );
    }
    disable() {}
}
