// esbuild transpiler output helpers
var __defProp = Object.defineProperty;
var __decorateClass = (decorators, target, key, kind) => {
  var result = kind > 1 ? void 0 : kind ? __defProp(target, key) : target;
  return result;
};

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

var TilingShellExtension = class extends Extension {
  enable() {
    this._settings = this.getSettings();
    this._handlerId = global.display.connect(
      'window-created',
      (display, currentlyActiveWindowParameter) => {
        this._onWindowCreated(currentlyActiveWindowParameter);
      }
    );
  }

  disable() {
    global.display.disconnect(this._handlerId);
    this._handlerId = null;
    this._settings = null;
  }

  _onWindowCreated(currentlyActiveWindowParameter) {
    log(currentlyActiveWindowParameter);
  }
};
