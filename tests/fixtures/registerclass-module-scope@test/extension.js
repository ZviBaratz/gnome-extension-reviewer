import GObject from 'gi://GObject';
import Clutter from 'gi://Clutter';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// GObject.registerClass at module scope returns a class, not an instance.
// This is the standard pattern for defining GObject subclasses in GJS.
export const MyEffect = new GObject.registerClass({
    GTypeName: "MyEffect",
    Properties: {
        'radius': GObject.ParamSpec.double(
            'radius', 'Radius', 'Blur radius',
            GObject.ParamFlags.READWRITE,
            0.0, 2000.0, 30.0
        ),
    },
}, class MyEffect extends Clutter.ShaderEffect {
    constructor(params) {
        super(params);
    }
});

export default class TestExtension extends Extension {
    enable() {
        this._effect = new MyEffect();
    }

    disable() {
        this._effect = null;
    }
}
