import * as Main from 'resource:///org/gnome/shell/ui/main.js';

// Helper class — constructor only runs when instantiated from enable()
export class TilingManager {
    constructor(monitorIndex) {
        // Shell globals in helper constructor: OK (only called from enable())
        this._workArea = Main.layoutManager.getWorkAreaForMonitor(monitorIndex);
        this._monitors = Main.layoutManager.monitors;
    }

    destroy() {
        this._workArea = null;
        this._monitors = null;
    }
}
