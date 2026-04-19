import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

// TRUE VIOLATION (FAIL): module-scope property assignment on Shell global —
// mutates Shell state outside enable().  Must remain FAIL.
Main.panel.someProperty = true;

export default class InitShellMutationExtension extends Extension {
    enable() {}
    disable() {}
}
