import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export default class MyExtension {
    enable(): void {
        console.log('Extension enabled');
    }
    disable(): void {
        console.log('Extension disabled');
    }
}
