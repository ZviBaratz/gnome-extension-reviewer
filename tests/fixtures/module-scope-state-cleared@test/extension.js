import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const cache = new Map();
const seen = new Set();
const refs = new WeakMap();

export default class StateExtension extends Extension {
    enable() {
        cache.set('key', 'value');
        seen.add('item');
    }

    disable() {
        cache.clear();
        seen.clear();
        // refs (WeakMap) does not need clearing — GC-friendly
    }
}
