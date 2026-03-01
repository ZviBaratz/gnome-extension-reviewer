import Gio from 'gi://Gio';

export class MyHelper {
    constructor() {
        // Runtime-only: this constructor runs when instantiated from enable()
        this._cancellable = new Gio.Cancellable();
        this._file = new Gio.File.new_for_path('/tmp/test');
    }

    destroy() {
        this._cancellable.cancel();
        this._cancellable = null;
        this._file = null;
    }
}
