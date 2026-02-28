import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class IgnoreTest extends Extension {
    enable() {
        // ego-lint-ignore-next-line: R-WEB-04
        const xhr = new XMLHttpRequest();
        document.querySelector('.foo'); // ego-lint-ignore: R-WEB-06
    }

    disable() {
    }
}
