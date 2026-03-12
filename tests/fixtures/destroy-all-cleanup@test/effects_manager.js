export class EffectsManager {
    add_effect(actor) {
        actor.connect('destroy', () => this._on_destroy(actor));
    }

    _on_destroy(actor) {
        // internal cleanup
    }

    destroy_all() {
        // centralized cleanup for all managed effects
    }
}
