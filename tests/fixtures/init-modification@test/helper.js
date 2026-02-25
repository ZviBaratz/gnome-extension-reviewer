import St from 'gi://St';

// BAD: Module-scope GObject constructor
const label = new St.Label({text: 'test'});

export function getLabel() {
    return label;
}
