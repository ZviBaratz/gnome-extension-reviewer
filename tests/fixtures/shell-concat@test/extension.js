import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        const proc = new Gio.Subprocess({argv: ['/bin/sh', '-c', '/bin/echo ' + this._value]});
    }
    disable() {}
}
