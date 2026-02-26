# Accessibility Checklist

> **Official guideline:** "Working accessibility is a hard requirement of a proper user interface, not a feature."

This checklist applies when an extension adds visible UI elements (panel indicators, Quick Settings, popups, dialogs, overlays).

---

## A1. Accessible Roles

Does every custom `St.Widget` subclass set an appropriate `accessible-role`?

- `St.Button` → `Atk.Role.PUSH_BUTTON` (built-in, automatic)
- `St.Label` → `Atk.Role.LABEL` (built-in, automatic)
- Custom toggle → `Atk.Role.TOGGLE_BUTTON`
- Custom slider → `Atk.Role.SLIDER`
- Container/panel → `Atk.Role.PANEL`
- Menu item → `Atk.Role.MENU_ITEM`

> **Reviewer says:** "Standard St widgets (St.Button, PopupMenu items) already have correct accessible roles. Only custom composite widgets need manual assignment."

## A2. Accessible Names

Are icon-only buttons and actionable widgets given `accessible-name`?

**Wrong:**
```javascript
let btn = new St.Button({
    child: new St.Icon({icon_name: 'edit-delete-symbolic'}),
});
```

**Correct:**
```javascript
let btn = new St.Button({
    child: new St.Icon({icon_name: 'edit-delete-symbolic'}),
    accessible_name: _('Delete'),
});
```

## A3. Label-Actor Relationships

Are `label-actor` relationships established for label/input pairs?

```javascript
let label = new St.Label({text: _('Brightness')});
let slider = new Slider.Slider(0.5);
slider.accessible_name = _('Brightness');
// Or use label-actor property if applicable
```

## A4. State Synchronization

Do toggle widgets maintain `Atk.StateType` in sync with visual state?

- `Atk.StateType.CHECKED` for checkboxes/toggles
- `Atk.StateType.SELECTED` for selectable items
- `Atk.StateType.SENSITIVE` for enabled/disabled state

> **Reviewer says:** "Built-in Quick Settings toggles handle Atk state automatically. Only flag if the extension creates custom toggle widgets that bypass QuickSettings.QuickToggle."

## A5. Built-in Widget Preference

Does the extension leverage built-in accessible widgets rather than reimplementing?

| Instead of | Use |
|---|---|
| Custom clickable `St.Bin` | `St.Button` |
| Custom toggle `St.Widget` | `QuickSettings.QuickToggle` |
| Custom menu | `PopupMenu.PopupMenuItem` |
| Custom slider | `Slider.Slider` |

## A6. Quick Settings Session Mode

Do Quick Settings items with settings access check `Main.sessionMode.allowSettings`?

```javascript
// Correct: hide preferences gear on lock screen
if (Main.sessionMode.allowSettings)
    this._addSettingsAction();
```

> **Reviewer says:** "This only applies to extensions that add Quick Settings menu items with a preferences gear/link. The item must not be accessible during locked sessions."

## A7. Keyboard Navigation

Are custom UI elements reachable via keyboard (Tab/Arrow keys)?

- `St.Button` and `PopupMenu` items are keyboard-navigable by default
- Custom widgets with `reactive: true` should be in the focus chain via `can_focus: true`

---

## Scoring

- **0 issues**: PASS — accessibility looks correct
- **1-2 issues**: ADVISORY — note specific improvements
- **3+ issues or missing accessible-name on primary actions**: BLOCKING — flag for remediation
