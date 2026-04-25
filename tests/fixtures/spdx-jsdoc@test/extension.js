// SPDX-FileCopyrightText: 2024 Test Author <test@example.com>
// SPDX-License-Identifier: GPL-2.0-or-later

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

/**
 * Calculate brightness as a percentage.
 * @param {number} current - current brightness value
 * @param {number} max - maximum brightness value
 * @returns {number} percentage (0-100)
 */
function calcBrightness(current, max) {
    return (current / max) * 100;
}

export default class SpdxJsdocExtension extends Extension {
    enable() {
        this._brightness = calcBrightness(50, 100);
    }

    disable() {
        this._brightness = null;
    }
}
