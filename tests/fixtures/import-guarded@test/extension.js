import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as utils from './utils.js';

export default class GuardedExtension extends Extension {
    async enable() {
        // Shell-only imports via guard — safe, prefs process gets null
        const Clutter = await utils.importInShellOnly('gi://Clutter');
        const St = await utils.importInShellOnly('gi://St');
        if (Clutter) {
            this._actor = new Clutter.Actor();
        }
    }

    disable() {
        this._actor = null;
    }
}
