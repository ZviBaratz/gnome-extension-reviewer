import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export default class DebugVolumeTest extends Extension {
    enable() {
        console.debug('e1');
        console.debug('e2');
        console.debug('e3');
        console.debug('e4');
        console.debug('e5');
        console.debug('e6');
        console.debug('e7');
        console.debug('e8');
        console.debug('e9');
        console.debug('e10');
        console.debug('e11');
        console.debug('e12');
        console.debug('e13');
        console.debug('e14');
        console.debug('e15');
        console.debug('e16');
        console.debug('e17');
        console.debug('e18');
        console.debug('e19');
        console.debug('e20');
        console.debug('e21');
        Main.notify('Alert 1');
        Main.notify('Alert 2');
        Main.notify('Alert 3');
        Main.notify('Alert 4');
    }

    disable() {
    }
}
