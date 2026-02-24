import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class WebApisExtension extends Extension {
    enable() {
        setTimeout(() => {}, 100);
        const xhr = new XMLHttpRequest();
        document.querySelector('.foo');
    }

    disable() {}
}
