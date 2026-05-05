import Shell from 'gi://Shell';
import Cogl from 'gi://Cogl';
import Clutter from 'gi://Clutter';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        this._hook = new Shell.SnippetHook();
        const focus = global.stage.get_key_focus();
        // Ternary version guard: Cogl.SnippetHook available on GNOME 48+
        const hook = Cogl.SnippetHook ? Cogl.SnippetHook.FRAGMENT : Shell.SnippetHook.FRAGMENT;
    }
    disable() {
        this._hook = null;
    }
}
