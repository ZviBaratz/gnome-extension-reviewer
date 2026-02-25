import Shell from 'gi://Shell';
import Clutter from 'gi://Clutter';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        this._hook = new Shell.SnippetHook();
        const focus = global.stage.get_key_focus();
    }
    disable() {
        this._hook = null;
    }
}
