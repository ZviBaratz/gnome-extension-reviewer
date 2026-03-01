import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {SignalTracker} from './signalTracker.js';

export default class SmartConnectExtension extends Extension {
    enable() {
        this._tracker = new SignalTracker();
        this._tracker.connectSmart(this._settings, 'changed::key1', () => {});
        this._tracker.connectSmart(this._settings, 'changed::key2', () => {});
        this._tracker.connectSmart(this._settings, 'changed::key3', () => {});
    }

    disable() {
        this._tracker.disconnectSmart();
        this._tracker = null;
    }
}
