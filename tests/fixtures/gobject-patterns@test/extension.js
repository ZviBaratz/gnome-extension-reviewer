import GObject from 'gi://GObject';
import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// Missing GTypeName
const MyWidget = GObject.registerClass(
class MyWidget extends St.BoxLayout {
    _init() {
        super._init();
    }
});

// Missing super._init
const BadWidget = GObject.registerClass(
class BadWidget extends St.BoxLayout {
    _init() {
        this._label = new St.Label({text: 'hello'});
    }
});

// Missing cr.$dispose in drawing callback
const DrawWidget = GObject.registerClass(
class DrawWidget extends St.DrawingArea {
    vfunc_repaint() {
        const cr = this.get_context();
        cr.setSourceRGBA(1, 0, 0, 1);
        cr.paint();
    }
});

export default class TestExtension extends Extension {
    enable() {}
    disable() {}
}
