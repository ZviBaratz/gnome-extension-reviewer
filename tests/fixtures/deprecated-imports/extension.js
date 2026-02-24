import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as ExtensionUtils from 'resource:///org/gnome/shell/misc/extensionUtils.js';
import * as Tweener from 'imports.tweener.tweener';
const Main = imports.ui.main;

export default class DeprecatedExtension extends Extension {
    enable() {
        ExtensionUtils.getSettings();
        Tweener.addTween(this, {});
        Main.panel.addToStatusArea('test', this);
    }

    disable() {}
}
