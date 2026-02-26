import {Extension, gettext as _} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class GettextConcatExtension extends Extension {
    enable() {
        // Bug: concatenation inside gettext breaks xgettext extraction
        this._label = _('Hello ' + this._getUserName());
    }

    _getUserName() {
        return 'World';
    }

    disable() {
        this._label = null;
    }
}
