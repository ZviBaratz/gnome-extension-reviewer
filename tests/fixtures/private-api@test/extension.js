import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export default class PrivateApiTest extends Extension {
    enable() {
        let indicators = Main.panel.statusArea.quickSettings._indicators;
        let system = Main.panel.statusArea.quickSettings._system;
    }

    disable() {
    }
}
