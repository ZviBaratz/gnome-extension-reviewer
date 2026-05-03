#!/usr/bin/env gjs
// Standalone GJS subprocess entry point — runs outside GNOME Shell.
// Intentionally uses legacy CJS-style imports.

const {Gio, GLib, Gtk} = imports.gi;

var mainWindow = null;

function init() {
    Gtk.init(null);
    mainWindow = new Gtk.Window({title: 'Desktop Icons'});
}
