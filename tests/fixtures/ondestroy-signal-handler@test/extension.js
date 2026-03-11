import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import St from 'gi://St';

export default class SignalHandlerExtension extends Extension {
    enable() {
        this._label = new St.Label({text: 'Hello'});
        this._label.connect('destroy', this._onDestroy.bind(this));
        this._setupWidget();
    }

    _setupWidget() {
        this._active = true;
    }

    // Many lines of code between .connect() and the handler definition
    // to ensure the guard-window (5 lines) cannot reach the connection

    _updateLabel() {
        if (this._active) {
            this._label.set_text('Updated');
        }
    }

    _refreshState() {
        this._active = false;
        this._updateLabel();
    }

    _processEvent() {
        if (!this._active) return;
        this._refreshState();
    }

    _handleInput() {
        this._processEvent();
    }

    _onDestroy() {
        this._active = false;
        this._label = null;
    }

    disable() {
        if (this._label) {
            this._label.destroy();
        }
    }
}
