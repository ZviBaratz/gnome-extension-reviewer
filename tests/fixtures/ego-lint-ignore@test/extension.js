import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class IgnoreTest extends Extension {
    enable() {
        // ego-lint-ignore-next-line: R-WEB-01
        setTimeout(() => {}, 1000);
        clearTimeout(this._id); // ego-lint-ignore: R-WEB-10
    }

    disable() {
    }
}
