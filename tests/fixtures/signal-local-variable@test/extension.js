import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class LocalVariableSignalExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._settingsId = this._settings.connect('changed::key', () => {});
    }

    _showNotification(text) {
        // Ephemeral local variable — signal is garbage collected with it
        let notification = new MessageTray.Notification(this._source, text);
        notification.connect('activated', () => {
            Main.extensionManager.openExtensionPrefs(this.uuid);
        });

        // Another ephemeral local signal
        let dialog = new ModalDialog.ModalDialog();
        dialog.connect('opened', () => log('dialog opened'));
    }

    disable() {
        this._settings.disconnect(this._settingsId);
        this._settings = null;
    }
}
