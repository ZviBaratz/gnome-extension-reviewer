import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

// TRUE VIOLATION: module-scope Shell global access
const primaryIdx = Main.layoutManager.primaryIndex;

// OK: arrow function definition is lazy (body not executed at module scope)
const getMonitors = () => Main.layoutManager.monitors;

// OK: async arrow function definition is lazy
const addItem = async () => Main.panel.addToStatusArea('test', null);

// OK: arrow function wrapping GObject constructor
const makeLabel = () => new St.Label({text: 'hello'});

export default class InitTimeTest extends Extension {
    enable() {
        // OK: Shell globals inside enable()
        Main.panel.addToStatusArea('test', this);
        this._monitors = getMonitors();
    }

    disable() {
        this._monitors = null;
    }
}
