const Main = imports.ui.main;
const Extension = imports.misc.extensionUtils.getCurrentExtension();

function enable() {
    Main.panel.addToStatusArea('test', {});
}

function disable() {}
