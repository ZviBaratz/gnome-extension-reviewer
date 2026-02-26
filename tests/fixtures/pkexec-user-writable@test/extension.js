import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gio from 'gi://Gio';

export default class PkexecUserWritableTest extends Extension {
    enable() {
        const proc = new Gio.Subprocess({
            argv: ['pkexec', '/home/user/helper.sh'],
        });
    }
    disable() {}
}
