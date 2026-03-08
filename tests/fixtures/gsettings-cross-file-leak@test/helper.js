import St from 'gi://St';

export class SliderHelper {
    constructor() {
        this._slider = new St.Slider();
        this._slider.connectObject(
            'notify::value', () => this._onValueChanged(),
            this
        );
    }

    _onValueChanged() {}

    destroy() {
        this._slider.disconnectObject(this);
        this._slider = null;
    }
}
