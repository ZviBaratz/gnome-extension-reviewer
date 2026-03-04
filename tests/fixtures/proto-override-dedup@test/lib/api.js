import * as BackgroundMenu from 'resource:///org/gnome/shell/ui/backgroundMenu.js';
import * as Search from 'resource:///org/gnome/shell/ui/search.js';

export class API {
    #originals = {};

    open() {
        // Override prototype — saves original first
        this.#originals['bgOpen'] = BackgroundMenu.BackgroundMenu.prototype.open;
        BackgroundMenu.BackgroundMenu.prototype.open = () => {};

        this.#originals['startSearch'] = Search.SearchController.prototype.startSearch;
        Search.SearchController.prototype.startSearch = () => {};
    }

    close() {
        // Restore originals
        BackgroundMenu.BackgroundMenu.prototype.open = this.#originals['bgOpen'];
        Search.SearchController.prototype.startSearch = this.#originals['startSearch'];
    }
}
