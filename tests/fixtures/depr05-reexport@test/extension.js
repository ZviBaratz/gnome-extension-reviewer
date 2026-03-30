// Re-export a local utility module under the name ExtensionUtils.
// This should NOT trigger R-DEPR-05 — the name is a local alias, not
// the deprecated ExtensionUtils global (removed in GNOME 45).
export * as ExtensionUtils from './extensionUtils.js';

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class TestExtension extends Extension {
    enable() {}
    disable() {}
}
