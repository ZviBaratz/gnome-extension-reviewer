import {Extension, gettext as _} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class GettextConcatLiteralExtension extends Extension {
    enable() {
        // OK: both operands are compile-time string literals on the same line
        // xgettext handles adjacent string literals correctly
        this._label = _('Hello ' + 'World');
        this._name = _("prefix_" + "suffix");
    }

    disable() {
        this._label = null;
        this._name = null;
    }
}
