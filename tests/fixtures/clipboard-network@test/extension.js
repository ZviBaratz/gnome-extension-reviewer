import St from 'gi://St';
import Soup from 'gi://Soup';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class ClipboardNetworkExtension extends Extension {
    enable() {
        this._clipboard = St.Clipboard.get_default();
        this._session = new Soup.Session();
    }

    disable() {
        this._session.abort();
        this._session = null;
        this._clipboard = null;
    }
}
