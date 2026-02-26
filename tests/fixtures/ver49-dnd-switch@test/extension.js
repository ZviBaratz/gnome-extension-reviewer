import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as DateMenu from 'resource:///org/gnome/shell/ui/dateMenu.js';

export default class DndExtension extends Extension {
    enable() {
        this._switch = new DateMenu.DoNotDisturbSwitch();
    }
    disable() {
        this._switch = null;
    }
}
