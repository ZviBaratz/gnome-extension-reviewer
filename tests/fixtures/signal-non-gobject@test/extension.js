import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class NonGObjectConnectExtension extends Extension {
    enable() {
        // Non-signal .connect() — e.g., IMAP or socket connection
        this._client = new ImapClient();
        this._client.connect(993, 'imap.example.com');

        // One real GObject signal connect + matching disconnect = balanced
        this._settings = this.getSettings();
        this._settingsId = this._settings.connect('changed::key', () => {});
    }

    disable() {
        this._settings.disconnect(this._settingsId);
        this._settings = null;
        this._client = null;
    }
}
