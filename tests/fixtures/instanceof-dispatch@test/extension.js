import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// Polymorphic dispatch — type check assigned to variable (should NOT fire R-SLOP-13)
const SharedMixin = {
    _redisplay() {
        const isFolder = this instanceof Object;
        const isAppDisplay = !isFolder;
        if (isFolder) {
            this._showFolderView();
        }
    },
};

export default class InstanceofDispatchExtension extends Extension {
    enable() {
        // Always-true instanceof check inside class method (SHOULD fire R-SLOP-13)
        if (this instanceof InstanceofDispatchExtension) {
            this._active = true;
        }
    }

    disable() {
        this._active = false;
    }
}
