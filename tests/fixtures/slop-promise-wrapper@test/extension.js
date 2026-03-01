import Gio from 'gi://Gio';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

function readFileAsync(path) {
    return new Promise((resolve, reject) => {
        const file = Gio.File.new_for_path(path);
        file.load_contents_async(null, (obj, res) => {
            try {
                const [ok, contents] = obj.load_contents_finish(res);
                resolve(contents);
            } catch (e) {
                reject(e);
            }
        });
    });
}

export default class PromiseWrapperExtension extends Extension {
    enable() {
        readFileAsync('/tmp/test').catch(console.error);
    }

    disable() {}
}
