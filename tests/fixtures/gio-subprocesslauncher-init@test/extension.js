import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// Module-scope subprocess launcher — configuration container, no open resources
const launcher = new Gio.SubprocessLauncher({
    flags: Gio.SubprocessFlags.STDOUT_PIPE,
});

export default class MyExtension extends Extension {
    enable() {
        this._proc = launcher.spawnv(['my-helper']);
    }

    disable() {
        this._proc?.force_exit();
        this._proc = null;
    }
}
