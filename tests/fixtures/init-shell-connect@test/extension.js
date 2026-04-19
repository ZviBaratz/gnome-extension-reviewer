import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

// ADVISORY (WARN): module-scope signal connection on Shell global — connects
// a lifecycle tracking signal, does not mutate Shell state.
// Pattern: blur-my-shell (Main.panel.connect('destroy', ...)).
Main.panel.connect('destroy', () => { cleanup(); });

export default class InitShellConnectExtension extends Extension {
    enable() {}
    disable() {}
}
