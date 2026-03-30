import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// Simulates Burn-My-Windows pattern: a helper class that passes a callback
// to a factory, and the callback receives a fresh object and connects to it.
// The `shader` parameter is a locally-created inner object — NOT `this`.
// constructor-resources should NOT fire for `shader.connect(...)`.
class ShaderHelper {
    constructor() {
        this.shaderFactory = new FakeFactory((shader) => {
            shader.connect('begin-animation', (s) => {
                s.doSomething();
            });
        });
    }
}

// Also: connecting on a parameter passed into a nested callback — not `this`.
class WrapperHelper {
    constructor(source) {
        source.addCallback((item) => {
            item.connect('notify::visible', () => {});
        });
    }
}

export default class InnerObjectExtension extends Extension {
    enable() {
        this._helper = new ShaderHelper();
    }
    disable() {
        this._helper = null;
    }
}
