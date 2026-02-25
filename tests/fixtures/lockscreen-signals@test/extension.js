import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class LockScreenSignalsExtension extends Extension {
    enable() {
        this._handlerId = global.stage.connect('key-press-event', () => {});
    }

    disable() {
        global.stage.disconnect(this._handlerId);
        this._handlerId = null;
    }
}
