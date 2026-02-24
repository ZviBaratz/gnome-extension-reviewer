import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class LoggingExtension extends Extension {
    enable() {
        log('legacy log function');
        print('debug output');
        printerr('error output');
    }

    disable() {}
}
