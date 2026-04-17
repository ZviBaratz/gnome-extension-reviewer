import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

// ADVISORY (WARN): module-scope const binding of Shell global — reads reference,
// does not mutate Shell state.  Pattern: caffeine-ng, GSConnect.
const QuickSettings = Main.panel.statusArea.quickSettings;

export default class InitShellReadConstExtension extends Extension {
    enable() {
        this._qs = QuickSettings;
    }

    disable() {
        this._qs = null;
    }
}
