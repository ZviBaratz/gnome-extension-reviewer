import St from 'gi://St';

export class RuntimeHelper {
    createLabel(text) {
        return new St.Label({text});
    }
}
