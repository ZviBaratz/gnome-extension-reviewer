import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class EmptyCatchCommentedExtension extends Extension {
    enable() {
        this._source = null;
    }

    _tryCleanup() {
        try {
            this._source.disconnect();
        } catch {
            // Already disconnected — safe to ignore
        }
    }

    disable() {
        this._tryCleanup();
        this._source = null;
    }
}
