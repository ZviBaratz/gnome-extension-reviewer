import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as ExtensionUtils from 'resource:///org/gnome/shell/misc/extensionUtils.js';
import * as Tweener from 'imports.tweener.tweener';

export default class DeprecatedExtension extends Extension {
    enable() {
        ExtensionUtils.getSettings();
        Tweener.addTween(this, {});
    }

    disable() {}
}
