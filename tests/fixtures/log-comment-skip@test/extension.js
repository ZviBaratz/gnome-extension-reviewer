import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {
        /* enable for troubleshooting: print('debug'); */
        // print('also commented out');
        console.debug('proper logging');
    }

    disable() {}
}
