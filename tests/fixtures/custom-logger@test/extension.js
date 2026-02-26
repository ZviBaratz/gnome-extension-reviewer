class Logger {
    static debug(msg) { console.log(`[DEBUG] ${msg}`); }
    static error(msg) { console.log(`[ERROR] ${msg}`); }
}

export default class TestExtension {
    enable() { Logger.debug('enabled'); }
    disable() { Logger.debug('disabled'); }
}
