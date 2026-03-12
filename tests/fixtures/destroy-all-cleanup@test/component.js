export class BlurComponent {
    constructor(effects) {
        this._effects = effects;
    }

    disable() {
        this._effects.destroy_all();
        this._effects = null;
    }
}
