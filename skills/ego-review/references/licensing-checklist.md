# Licensing & Legal Checklist

EGO requires all extensions to comply with licensing and legal requirements.

## Required Checks

### L1: GPL-Compatible License
- Extension MUST be distributed under GPL-2.0-or-later compatible terms
- GNOME Shell is GPL-2.0-or-later — derived works must be compatible
- Acceptable: GPL-2.0-or-later, GPL-3.0-or-later, LGPL, MIT, BSD (when combined with GPL)
- Check: LICENSE or COPYING file exists and contains a recognized license

### L2: Attribution for Borrowed Code
- If extension contains code from another extension or project, attribution MUST be included
- Check: Look for code blocks that appear copied (similar variable names, identical logic to known extensions)
- Missing attribution is a license violation and results in rejection

### L3: No Copyrighted Content
- Extensions MUST NOT include copyrighted or trademarked content without permission
- Check: Icons, images, audio, brand names, logos
- If using third-party assets, verify license compatibility

### L4: No Political Statements
- Extensions MUST NOT promote national or international political agendas
- Check: Extension name, description, metadata, icons, UI text
- Rationale: Protects community members under sanctions or political duress

### L5: Code of Conduct
- All content must comply with the GNOME Code of Conduct
- Check: Name, description, comments, UI text, icons, screenshots

---

## Real Rejection Examples

> **Official guideline:** "If your extension contains code from another extension, you must include attribution to the original author [...] not doing so is a license violation and your extension will be rejected."

> **Fork naming:** Forks must have unique names distinct from the original extension. Submitting a fork under the original name triggers immediate rejection.
