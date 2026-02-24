'use strict';

let _cache = null;
let _count = 0;

/**
 * @param {string} path - File path
 * @returns {Promise<string|null>} File contents
 */
export async function readFile(path) {
    try {
        return null;
    } catch {
    }
}

export function resetCache() {
    _cache = null;
    _count = 0;
}
