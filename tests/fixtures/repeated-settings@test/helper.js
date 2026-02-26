export function loadConfig(ext) {
    const settings = ext.getSettings();
    return settings.get_string('config-key');
}
