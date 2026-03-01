import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export function _helperFunction() {
    return true;
}

export const _DEFAULT_TIMEOUT = 5000;

export default class UnderscoreExportExtension extends Extension {
    enable() {
        this._value = _helperFunction();
    }

    disable() {
        this._value = null;
    }
}
