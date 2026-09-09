# audit-accessibility

## When to Use
Run on any web_artifact before publishing. Also can be invoked manually on any HTML/React code.

## Workflow

1. **Parse** — Load the artifact's content (HTML or React JSX)
2. **Run WCAG 2.1 AA Checks**:
   - **Contrast**: foreground vs background, muted text vs background
   - **Focus states**: verify `:focus-visible` or `focus:ring` on all interactive elements
   - **Semantics**: check for `<header>`, `<nav>`, `<main>`, `<footer>` landmarks
   - **Images**: check for `alt` attributes
   - **Keyboard**: verify `tabindex`, ARIA roles, keyboard handlers
   - **Forms**: check for `<label>` associations
   - **Headings**: verify h1→h6 hierarchy (no skipped levels)

3. **Score** — Start at 100, deduct per severity:
   - P0 (critical): -30 (contrast < 3:1, no focus states)
   - P1 (high): -15 (contrast < 4.5:1, missing landmarks)
   - P2 (medium): -5 (missing alt text, heading hierarchy)
   - P3 (low): -2 (best practice suggestions)

4. **Create Design Review** — Call `auditA11y` backend function with artifact_id

5. **Report** — Return issues grouped by severity with remediation suggestions

## Pass Criteria
- Score ≥ 90
- 0 P0 issues
- 0 P1 issues
- P2/P3 issues logged but non-blocking

## Fail Handling
- Return issues with specific remediation code
- Do not auto-publish failed artifacts
- After 2 consecutive failures, escalate to Rojs
