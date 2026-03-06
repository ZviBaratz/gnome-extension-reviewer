import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as MessageTray from 'resource:///org/gnome/shell/ui/messageTray.js';

export default class MessageTrayLeakExtension extends Extension {
    enable() {
        this._source = new MessageTray.Source({title: 'Test'});
        Main.messageTray.add(this._source);
    }

    disable() {
        this._source = null;
    }
}
