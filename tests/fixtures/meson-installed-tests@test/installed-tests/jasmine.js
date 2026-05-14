// Jasmine test runner (dev-only, never shipped in EGO package)
function evalSpec(code) {
    return eval(code);  // eval used in test infra — not extension code
}
