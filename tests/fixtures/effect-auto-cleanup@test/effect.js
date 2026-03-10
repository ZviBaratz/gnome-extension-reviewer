import GObject from 'gi://GObject';
import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';

class BlurEffect extends Clutter.Effect {
    _init() {
        super._init();
        this._settings = new Gio.Settings({schema_id: 'org.test.blur'});
        this._handlerId = this._settings.connect('changed', () => {
            this._updateEffect();
        });
    }

    _updateEffect() {
        // Reconfigure effect based on settings
    }
}

export {BlurEffect};

export default GObject.registerClass(
    {GTypeName: 'TestBlurEffect'},
    BlurEffect,
);
