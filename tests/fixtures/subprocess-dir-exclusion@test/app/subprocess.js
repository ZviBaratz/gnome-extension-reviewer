#!/usr/bin/env gjs
// Standalone GJS subprocess entry point — runs outside GNOME Shell.
// Intentionally uses legacy CJS-style imports and lifecycle patterns that
// would be flagged as leaks in Shell extension code but are normal here.

const {Gio, GLib, Gtk} = imports.gi;

var mainWindow = null;
var _settings = new Gio.Settings({schema_id: 'org.desktop.icons'});
var _connId = _settings.connect('changed', () => {});

function init() {
    Gtk.init(null);
    mainWindow = new Gtk.Window({title: 'Desktop Icons'});
}
