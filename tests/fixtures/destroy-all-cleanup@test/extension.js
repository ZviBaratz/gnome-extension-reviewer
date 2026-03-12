import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {EffectsManager} from './effects_manager.js';
import {BlurComponent} from './component.js';

export default class TestExtension extends Extension {
    enable() {
        this._effects = new EffectsManager();
        this._component = new BlurComponent(this._effects);
    }

    disable() {
        this._component.disable();
        this._component = null;
        // _effects cleanup is delegated to component — no direct reference here
    }
}
