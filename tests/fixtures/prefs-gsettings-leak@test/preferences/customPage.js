// Preferences page with bare GSettings connect (transient window — GC'd on close)
export function buildPage(settings) {
    const id1 = settings.connect('changed::theme', () => {
        updatePreview();
    });
    const id2 = settings.connect('changed::size', () => {
        updateSize();
    });
    const id3 = settings.connect('changed::position', () => {
        updatePosition();
    });
}
