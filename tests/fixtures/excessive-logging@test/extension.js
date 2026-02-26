import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class LogExt extends Extension {
    enable() {
        console.debug('step 1');
        console.debug('step 2');
        console.debug('step 3');
        console.debug('step 4');
        console.debug('step 5');
        console.debug('step 6');
        console.debug('step 7');
        console.debug('step 8');
        console.log('info 1');
        console.log('info 2');
        console.log('info 3');
        console.log('info 4');
        console.log('info 5');
        console.log('info 6');
        console.log('info 7');
        console.log('info 8');
    }
    disable() {}
}
