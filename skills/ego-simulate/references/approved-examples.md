# Approved Extension Patterns

Idiomatic patterns that EGO reviewers consider well-written. Use these as
positive examples when generating simulation reports — note where the extension
under review follows or deviates from these patterns.

## Clean Lifecycle

```javascript
export default class MyExtension extends Extension {
    enable() {
        this._indicator = new PanelMenu.Button(0.0, this.metadata.name);
        Main.panel.addToStatusArea(this.uuid, this._indicator);
    }

    disable() {
        this._indicator?.destroy();
        this._indicator = null;
    }
}
```

*Why reviewers like it: Perfect symmetry — create in enable, destroy in
disable. Optional chaining handles rapid enable/disable.*

## Signal Management with connectObject

```javascript
enable() {
    this._settings = this.getSettings();
    this._settings.connectObject(
        'changed::show-indicator', () => this._updateVisibility(),
        'changed::refresh-interval', () => this._resetTimer(),
        this
    );
}

disable() {
    this._settings?.disconnectObject(this);
    this._settings = null;
}
```

*Why reviewers like it: connectObject auto-disconnects all signals when the
owner is destroyed. No manual signal ID tracking needed.*

## Timeout Handling

```javascript
enable() {
    this._refreshTimer();
}

_refreshTimer() {
    this._removeTimer();
    this._timerId = GLib.timeout_add_seconds(
        GLib.PRIORITY_DEFAULT,
        this._interval,
        () => {
            this._refresh();
            return GLib.SOURCE_CONTINUE;
        }
    );
}

_removeTimer() {
    if (this._timerId) {
        GLib.Source.remove(this._timerId);
        this._timerId = 0;
    }
}

disable() {
    this._removeTimer();
}
```

*Why reviewers like it: Timer ID stored, explicit SOURCE_CONTINUE return,
cleanup in disable, guard against double-remove.*

## Gettext (correct pattern)

```javascript
// In extension.js
import {Extension, gettext as _} from
    'resource:///org/gnome/shell/extensions/extension.js';

export default class MyExtension extends Extension {
    enable() {
        const label = _('Settings');
    }
}

// In prefs.js
import {ExtensionPreferences, gettext as _} from
    'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';
```

*Why reviewers like it: Uses the Extension/ExtensionPreferences gettext, not
Gettext.dgettext(). Proper i18n integration.*

## Preferences with Adwaita

```javascript
import Adw from 'gi://Adw';
import {ExtensionPreferences} from
    'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class MyPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const page = new Adw.PreferencesPage();
        const group = new Adw.PreferencesGroup({title: 'General'});

        const row = new Adw.SwitchRow({
            title: 'Enable Feature',
            subtitle: 'Toggle the main feature',
        });

        this.getSettings().bind(
            'enable-feature', row, 'active',
            Gio.SettingsBindFlags.DEFAULT
        );

        group.add(row);
        page.add(group);
        window.add(page);
    }
}
```

*Why reviewers like it: Uses Adw widgets (not raw GTK), fillPreferencesWindow
(not getPreferencesWidget), settings bind for automatic sync.*

## Async with _destroyed Guard

```javascript
async enable() {
    this._destroyed = false;
    this._cancellable = new Gio.Cancellable();

    try {
        const data = await this._fetchData(this._cancellable);
        if (this._destroyed) return;
        this._processData(data);
    } catch (e) {
        if (!e.matches(Gio.IOErrorEnum, Gio.IOErrorEnum.CANCELLED))
            console.error('MyExt: fetch failed', e);
    }
}

disable() {
    this._destroyed = true;
    this._cancellable?.cancel();
    this._cancellable = null;
}
```

*Why reviewers like it: _destroyed check after every await, Gio.Cancellable
for abortable operations, terse error message.*
