import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

/**
 * @param {string} name - The name parameter
 * @returns {boolean} Whether the operation succeeded
 */
function doSomething(name) {
    return name !== null;
}

/**
 * @param {number} value - A numeric value
 * @param {string} label - A string label
 * @returns {string} The formatted result
 */
function formatValue(value, label) {
    return `${label}: ${value}`;
}

export default class TsconfigJsdocExtension extends Extension {
    enable() {
        this._result = doSomething('test');
        this._text = formatValue(42, 'answer');
    }

    disable() {
        this._result = null;
        this._text = null;
    }
}
