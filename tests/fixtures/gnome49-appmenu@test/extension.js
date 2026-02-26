import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export default class Gnome49AppMenuTest extends Extension {
    enable() {
        this._button = Main.panel.statusArea.AppMenuButton;
    }
    disable() {
        this._button = null;
    }
}
