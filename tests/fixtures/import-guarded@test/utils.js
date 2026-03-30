// Conditional import utilities — safe guard pattern used by Burn-My-Windows and similar extensions.
// These functions ensure Shell-only modules never load in the prefs process (and vice versa).

export async function importInShellOnly(module) {
  if (typeof global !== 'undefined') {
    return (await import(module)).default;
  }
  return null;
}

export async function importInPrefsOnly(module) {
  if (typeof global === 'undefined') {
    return (await import(module)).default;
  }
  return null;
}
