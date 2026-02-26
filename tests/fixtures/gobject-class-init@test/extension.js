import GObject from 'gi://GObject';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as QuickSettings from 'resource:///org/gnome/shell/ui/quickSettings.js';

// GObject.registerClass class — constructor should NOT be flagged
const MyToggle = GObject.registerClass(
    class MyToggle extends QuickSettings.QuickMenuToggle {
        constructor(settings) {
            super();
            // These are fine — only instantiated during enable()
            this._icon = new St.Icon({icon_name: 'test'});
            this._label = new St.Label({text: 'test'});
            const menu = Main.panel.statusArea.quickSettings;
        }
    }
);

// BAD: Module-scope Shell modification — should still be flagged
Main.panel.addToStatusArea('test', null);

export default class TestExtension extends Extension {
    enable() {
        this._toggle = new MyToggle(this.getSettings());
    }

    disable() {
        this._toggle?.destroy();
        this._toggle = null;
    }
}
