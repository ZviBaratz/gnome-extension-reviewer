import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class SlopErrorInstanceofTest extends Extension {
    enable() {
        try {
            this._init();
        } catch (e) {
            if (e instanceof TypeError) {
                console.error('Type error:', e.message);
            }
        }
    }
    disable() {}
}
