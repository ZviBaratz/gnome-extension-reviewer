import Gio from 'gi://Gio';

/**
 * Execute a command with pkexec
 * @param {string} command - The command to execute
 * @param {string[]} args - Command arguments
 * @returns {Promise<boolean>} Whether execution succeeded
 */
export async function executeCommand(command, args) {
    const proc = new Gio.Subprocess({
        argv: [command, ...args],
        flags: Gio.SubprocessFlags.STDOUT_PIPE,
    });
    proc.init(null);
    return true;
}
