import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class AutoInstallExtension extends Extension {
    enable() {
        let proc1 = Gio.Subprocess.new(['/bin/sh', '-c', 'pip install requests'], Gio.SubprocessFlags.NONE);
        let proc2 = Gio.Subprocess.new(['/bin/sh', '-c', 'npm install lodash'], Gio.SubprocessFlags.NONE);
        let proc3 = Gio.Subprocess.new(['/bin/sh', '-c', 'apt install curl'], Gio.SubprocessFlags.NONE);
    }

    disable() {}
}
