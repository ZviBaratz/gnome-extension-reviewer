import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class ConsoleLogExtension extends Extension {
    enable() {
        console.log('Extension enabled');
    }

    disable() {
        console.log('Extension disabled');
    }
}
