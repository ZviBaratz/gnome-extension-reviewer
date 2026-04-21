/* sql.js - v1.10.2
 * This file was downloaded from https://github.com/sql-js/sql.js/releases/tag/v1.10.2
 */
// Simulates a vendored SQLite WebAssembly port with browser-compat shims.
// Would trigger R-WEB-03/04/06/07/09 and prototype-override if not excluded.

var fetch = typeof fetch !== 'undefined' ? fetch : null;  // R-WEB-03 trigger
var XMLHttpRequest = typeof XMLHttpRequest !== 'undefined' ? XMLHttpRequest : null;  // R-WEB-04 trigger
var window = typeof window !== 'undefined' ? window : null;  // R-WEB-07 trigger
var document = typeof document !== 'undefined' ? document : null;  // R-WEB-06 trigger

Object.prototype.toString = function() { return '[vendored]'; };  // prototype-override trigger
