import Soup from 'gi://Soup';

export default class TestExtension {
    enable() {
        this._session = new Soup.Session();
    }

    disable() {
        this._session = null;
    }
}
