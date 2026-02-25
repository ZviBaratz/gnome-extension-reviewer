import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Shell from 'gi://Shell';

export default class Gnome46ExtrasTest extends Extension {
    enable() {
        this._blur = new Shell.BlurEffect({sigma: 20});
        this._blur.sigma = 30;
    }

    disable() {
        this._blur = null;
    }
}
