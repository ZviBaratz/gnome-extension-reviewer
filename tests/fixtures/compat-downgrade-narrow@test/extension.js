import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// No backward-compat excuse: targets only GNOME 45-48
export default class TestExtension extends Extension {
    enable() {
        Meta.later_add(Meta.LaterType.BEFORE_REDRAW, () => {});
    }

    disable() {}
}
