import Soup from 'gi://Soup';
import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// Default param: new Soup.Session() is call-time, not module-load-time.
// Should NOT trigger init/shell-modification.
async function fetchData(url, session = new Soup.Session()) {
    const msg = Soup.Message.new('GET', url);
    const bytes = await session.send_and_read_async(msg, 0, null);
    return new TextDecoder().decode(bytes.get_data());
}

// async function with Gio default param — also call-time.
async function request(url, cancellable = new Gio.Cancellable()) {
    // ...
}

export default class MyExtension extends Extension {
    enable() {
        fetchData('https://example.com');
    }

    disable() {}
}
