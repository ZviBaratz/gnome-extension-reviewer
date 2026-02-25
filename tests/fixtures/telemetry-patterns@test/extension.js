import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TelemetryExt extends Extension {
    enable() {
        this._analytics = new Map();
        this.trackEvent('enable', {});
    }
    trackEvent(name, data) {
        this._analytics.set(name, data);
    }
    disable() {
        this._analytics = null;
    }
}
