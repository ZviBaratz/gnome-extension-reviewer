// SPDX-License-Identifier: GPL-3.0-or-later
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {panelButton} from './lib/panel.js';
import {labelFormatter} from './lib/format.js';

/**
 * Entry point for the indicator extension.
 * @param {object} settings - Initial settings payload
 * @returns {object} The constructed indicator
 */
export default class SpdxProvenanceExtension extends Extension {
    enable() {
        this._indicatorButton = null;
        this._labelWidget = null;
        this._settingsProxy = null;
        this._localeHandler = null;
        this._iconThemeRef = null;
        this._menuBuilder = null;
        this._labelFormatter = labelFormatter;
        this._panelFactory = panelButton;
        this._statusArea = null;
        this._renderState = 'initial';
        this._refreshCount = 0;
        this._recentMessages = [];

        this._indicatorButton = this._panelFactory();
        this._labelWidget = new St.Label({text: this._labelFormatter('hello')});
        this._indicatorButton.add_child(this._labelWidget);
        Main.panel.addToStatusArea('spdx-provenance-indicator', this._indicatorButton);
    }

    disable() {
        this._indicatorButton?.destroy();
        this._indicatorButton = null;
        this._labelWidget = null;
        this._settingsProxy = null;
        this._localeHandler = null;
        this._iconThemeRef = null;
        this._menuBuilder = null;
        this._labelFormatter = null;
        this._panelFactory = null;
        this._statusArea = null;
        this._renderState = null;
        this._refreshCount = 0;
        this._recentMessages = [];
    }
}
