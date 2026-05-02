import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

/**
 * Parse document.querySelectorAll results into an array.
 * This is a JSDoc comment — document. here must NOT trigger R-WEB-06.
 */
export default class WebApisExtension extends Extension {
    enable() {
        setTimeout(() => {}, 100);
        const xhr = new XMLHttpRequest();
        document.querySelector('.foo'); // real DOM call — MUST trigger R-WEB-06
        clearTimeout(this._timer);
        clearInterval(this._interval);
    }

    disable() {}
}

async function fetchLinkPreview(url) {
    const document = await parseMetadata(url); // local var — must NOT trigger R-WEB-06
    const title = document.title;              // local var access — must NOT trigger R-WEB-06
    const desc = document.description;        // local var access — must NOT trigger R-WEB-06
    return { title, desc };
}
