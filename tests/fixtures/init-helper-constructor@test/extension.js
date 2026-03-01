import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {MyHelper} from './helper.js';

export default class InitHelperExtension extends Extension {
    enable() {
        this._helper = new MyHelper();
    }

    disable() {
        this._helper.destroy();
        this._helper = null;
    }
}
