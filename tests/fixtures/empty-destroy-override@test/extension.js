import GObject from 'gi://GObject';
import St from 'gi://St';

const MyWidget = GObject.registerClass(
class MyWidget extends St.Widget {
    destroy() { super.destroy(); }
});

export default class TestExtension {
    enable() { this._widget = new MyWidget(); }
    disable() { this._widget.destroy(); this._widget = null; }
}
