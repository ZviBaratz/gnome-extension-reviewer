import {Extension, gettext as Gettext} from 'resource:///org/gnome/shell/extensions/extension.js';

const _ = Gettext.dgettext('wrong-domain', 'Hello');

export default class GettextExt extends Extension {
    enable() {}
    disable() {}
}
