import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {loadIcon} from './lib/iconHelper.js';

export default class TestExtension extends Extension {
    enable() {
        this._icon = loadIcon('/tmp/icon.png');
    }

    disable() {
        this._icon = null;
    }
}
