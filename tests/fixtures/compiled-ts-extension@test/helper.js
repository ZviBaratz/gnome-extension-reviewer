// Compiled helper class — no explicit destroy method
// In compiled TypeScript, cleanup is handled by parent class hierarchy

import GLib from 'gi://GLib';

var __publicField = (obj, key, value) => {
  __defProp(obj, key, {value, writable: true});
  return value;
};

export class WindowTracker {
  constructor() {
    this._timeoutId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, () => {
      return GLib.SOURCE_CONTINUE;
    });
    this._signalId = global.display.connect('notify::focus-window', () => {});
  }
}
