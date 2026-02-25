import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class LoggingVolumeTest extends Extension {
    enable() {
        console.debug('d1');
        console.debug('d2');
        console.debug('d3');
        console.debug('d4');
        console.debug('d5');
        console.warn('w1');
        console.warn('w2');
        console.warn('w3');
        console.warn('w4');
        console.warn('w5');
        console.error('e1');
        console.error('e2');
        console.error('e3');
        console.error('e4');
        console.error('e5');
        console.info('i1');
        console.info('i2');
        console.info('i3');
        console.info('i4');
        console.info('i5');
        console.debug('d6');
        console.debug('d7');
        console.debug('d8');
        console.debug('d9');
        console.debug('d10');
        console.warn('w6');
        console.warn('w7');
        console.warn('w8');
        console.warn('w9');
        console.warn('w10');
        console.error('e6');
        console.error('e7');
        console.error('e8');
        console.error('e9');
        console.error('e10');
    }

    disable() {
    }
}
