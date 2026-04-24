// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Format a greeting for the panel label.
 * @param {string} name - The name to greet
 * @returns {string} The formatted label text
 */
export function labelFormatter(name) {
    const trimmed = typeof name === 'string' ? name.trim() : '';
    return trimmed ? `Hello, ${trimmed}!` : 'Hello!';
}
