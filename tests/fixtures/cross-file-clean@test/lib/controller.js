import Gio from 'gi://Gio';
import GLib from 'gi://GLib';

export class Controller {
    enable() {
        this._timeoutId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 60, () => {
            return GLib.SOURCE_CONTINUE;
        });
        const file = Gio.File.new_for_path('/tmp/test');
        this._monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, null);
    }

    destroy() {
        if (this._timeoutId) {
            GLib.Source.remove(this._timeoutId);
            this._timeoutId = null;
        }
        this._monitor.cancel();
        this._monitor = null;
    }
}
