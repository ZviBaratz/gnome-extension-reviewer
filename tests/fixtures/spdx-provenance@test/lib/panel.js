// SPDX-License-Identifier: GPL-3.0-or-later
import St from 'gi://St';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

/**
 * Build a panel button with the default style class.
 * @returns {PanelMenu.Button} A new panel button instance
 */
export function panelButton() {
    const button = new PanelMenu.Button(0.0, 'spdx-provenance-indicator', false);
    button.add_style_class_name('spdx-provenance-indicator');
    return button;
}
