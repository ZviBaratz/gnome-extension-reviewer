import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class StageChildExtension extends Extension {
    enable() {
        this._label = new St.Label({text: 'Hello'});
        global.stage.add_child(this._label);
    }

    disable() {
        this._label = null;
    }
}
