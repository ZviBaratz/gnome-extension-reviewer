import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// The original animations used Tweener instead of Clutter animations
// this._settings = ExtensionUtils.getSettings('org.test.extension');
/* ExtensionUtils was the old way */

export default class CommentTestExtension extends Extension {
    enable() {}
    disable() {}
}
