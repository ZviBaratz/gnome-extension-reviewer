// Backward-compat code: targets GNOME 42-48
// Uses legacy imports (valid for GNOME 42)
const Main = imports.ui.main;

function enable() {
    Meta.later_add(Meta.LaterType.BEFORE_REDRAW, () => {});
}

function disable() {}
