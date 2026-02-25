import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {gettext as Gettext} from 'gettext';

const _ = (s) => Gettext.dgettext('gettext-direct', s);

export default class GettextTest extends Extension {
    enable() {
        console.debug(_('enabled'));
    }

    disable() {
    }
}
