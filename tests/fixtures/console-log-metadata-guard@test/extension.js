// SPDX-License-Identifier: GPL-2.0-or-later
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import {debugLog} from './debug.js';

export default class TestExtension extends Extension {
    enable() {
        debugLog('enabled');
    }

    disable() {
        debugLog('disabled');
    }
}
