import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';

export default class TestExtension extends Extension {
    enable() {
        PopupMenu.PopupMenuItem.prototype._originalActivate = PopupMenu.PopupMenuItem.prototype.activate;
        PopupMenu.PopupMenuItem.prototype.activate = function() {
            return;
        };
    }

    disable() {
        // Missing restoration of prototype!
    }
}
