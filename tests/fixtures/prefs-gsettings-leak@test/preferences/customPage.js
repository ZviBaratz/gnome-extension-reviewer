// Preferences page with bare GSettings connect (transient window — GC'd on close)
export function buildPage(settings) {
    settings.connect('changed::theme', () => {
        updatePreview();
    });
    settings.connect('changed::size', () => {
        updateSize();
    });
    settings.connect('changed::position', () => {
        updatePosition();
    });
}
