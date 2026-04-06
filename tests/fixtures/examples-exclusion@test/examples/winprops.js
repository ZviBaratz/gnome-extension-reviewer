// Example: customize window properties for PaperWM
// This file uses the old imports.* API for GNOME 44 compatibility.
// It is NOT part of the extension runtime.
const GLib = imports.gi.GLib;
const Meta = imports.gi.Meta;
const Shell = imports.gi.Shell;
const St = imports.ui.st;

// Example: make terminal windows always float
function init(ext) {
    ext.winprops.forEach(function(p) {
        if (p.wm_class === "Alacritty") {
            p.float = true;
        }
    });
}
