import GdkPixbuf from 'gi://GdkPixbuf';

export function loadIcon(path) {
    return GdkPixbuf.Pixbuf.new_from_file(path);
}
