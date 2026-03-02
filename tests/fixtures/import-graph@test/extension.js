import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {RuntimeHelper} from './lib/runtime.js';
import {getVersion} from './lib/shared.js';

export default class ImportGraphExtension extends Extension {
    enable() {
        this._helper = new RuntimeHelper();
    }

    disable() {
        this._helper = null;
    }
}
