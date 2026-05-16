import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class DynamicSchemaIdExtension extends Extension {
    enable() {
        // Dynamic variable as schema_id — should NOT trigger R-SLOP-24
        // (reading arbitrary schemas from other sources, e.g. settings migration)
        for (const schemaId of this._externalSchemas) {
            const settings = new Gio.Settings({ schema_id: schemaId });
            this._cache.set(schemaId, settings);
        }

        // Function parameter as schema_id — should NOT trigger R-SLOP-24
        this._loadSettings(this._schemaId);
    }

    _loadSettings(id) {
        return new Gio.Settings({ schema_id: id });
    }

    disable() {
        this._cache = null;
    }
}
