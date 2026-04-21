import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import Gi from 'gi://GIRepository';

// Gi.require() is the GJS introspection API for optional namespace loading.
// It is a method call (Gi.require), NOT a standalone require() — must NOT trigger R-WEB-09.
const GLibUnix = Gi.require('GLibUnix', '2.0');

export default class GiRequireFpTest extends Extension {
    enable() {
        // Using an optional namespace loaded via Gi.require
        if (GLibUnix) {
            GLibUnix.set_fd_nonblocking(0, true);
        }
    }

    disable() {}
}
