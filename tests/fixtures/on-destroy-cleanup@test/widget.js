import GObject from 'gi://GObject';
import GLib from 'gi://GLib';
import St from 'gi://St';

class TestWidget extends St.BoxLayout {
    constructor() {
        super();
        this._sourceId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 5, () => {
            return GLib.SOURCE_CONTINUE;
        });
        this.connect('destroy', this.onDestroy.bind(this));
    }

    onDestroy() {
        if (this._sourceId) {
            GLib.Source.remove(this._sourceId);
            this._sourceId = null;
        }
    }
}

export default GObject.registerClass(
    { GTypeName: 'TestWidget' },
    TestWidget,
);
