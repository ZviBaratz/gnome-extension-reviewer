import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

var globalCounter = 0;

export default class VarExt extends Extension {
    enable() {
        var localVar = 1;
        globalCounter = localVar;
    }
    disable() {}
}
