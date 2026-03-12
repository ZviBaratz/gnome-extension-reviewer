import Gio from 'gi://Gio';

export class EffectsDialog {
    constructor(settings) {
        this._settings = settings;
        this._settings.connect('changed::sigma', () => {
            this._updateSigma();
        });
        this._settings.connect('changed::brightness', () => {
            this._updateBrightness();
        });
    }

    _updateSigma() {}
    _updateBrightness() {}
}
