// SPDX-License-Identifier: GPL-2.0-or-later
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const metadata = Extension.lookupByURL(import.meta.url)?.metadata ?? {};

export function debugLog(msg) {
    if (metadata['build-type'] === 'debug')
        console.log(`[TestExt] ${msg}`);
}
