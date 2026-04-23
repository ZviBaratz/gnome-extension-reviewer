import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

/**
 * Calculate power percentage.
 * @param {number} current - current level
 * @param {number} max - max level
 * @returns {number} percentage
 */
function calcPercent(current, max) {
    return (current / max) * 100;
}

export default class TsConfigJsdocExtension extends Extension {
    enable() {
        this._value = calcPercent(50, 100);
    }

    disable() {
        this._value = null;
    }
}
