import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const cache = new Map();
const seen = new Set();

export default class StateExtension extends Extension {
    enable() {
        cache.set('key', 'value');
        seen.add('item');
    }

    disable() {
        // no clear() calls — state leaks across cycles
    }
}
