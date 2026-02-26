import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class CurlSpawnExtension extends Extension {
    enable() {
        const proc = Gio.Subprocess.new(['curl', 'https://api.example.com'], 0);
        const proc2 = Gio.Subprocess.new(['gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', 'prefer-dark'], 0);
    }

    disable() {}
}
