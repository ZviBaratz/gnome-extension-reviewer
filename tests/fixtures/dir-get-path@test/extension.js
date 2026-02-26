export default class TestExtension {
    enable() {
        const path = this.dir.get_path();
        console.debug(`Extension path: ${path}`);
    }
    disable() {}
}
