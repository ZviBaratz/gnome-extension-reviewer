import Gtk from 'gi://Gtk';

// Shared module imported by both extension.js and prefs.js
// Should still FAIL since it's reachable from extension.js
export function getVersion() {
    return '1.0';
}
