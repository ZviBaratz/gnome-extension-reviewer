import Soup from 'gi://Soup';

export default class TestExtension {
    enable() {
        this._session = new Soup.Session();
        let msg = new Soup.Message({ method: 'GET', uri: GLib.Uri.parse('https://example.com', GLib.UriFlags.NONE) });
        this._session.send_and_read_async(msg, GLib.PRIORITY_DEFAULT, null, null);
    }

    disable() {
        this._session.abort();
        this._session = null;
    }
}
