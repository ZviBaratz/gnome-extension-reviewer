import Gtk from 'gi://Gtk';
import Adw from 'gi://Adw';

export function buildPrefsPage(settings) {
    const page = new Adw.PreferencesPage();
    const group = new Adw.PreferencesGroup({title: 'Settings'});
    page.add(group);
    return page;
}
