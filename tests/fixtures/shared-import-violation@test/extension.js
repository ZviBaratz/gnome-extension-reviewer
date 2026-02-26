import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {makeLabel} from './utils.js';

export default class SharedImportExtension extends Extension {
    enable() {
        this._label = makeLabel('Hello');
    }

    disable() {
        this._label = null;
    }
}
