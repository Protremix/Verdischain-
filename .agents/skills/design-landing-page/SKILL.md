# design-landing-page

## When to Use
When the user requests a landing page for either Verdis Chain or EvolvixOS.

## Workflow

1. **Clarify** — Ask (if not provided):
   - Which project: `verdis` or `evolvixos`?
   - What is the primary purpose (product showcase, token sale, docs portal)?
   - Who is the target audience?

2. **Select Theme** — Load the project's default dark-first theme:
   - Verdis → `Verdis Dark` (green/black, #00ff88 primary)
   - EvolvixOS → `EvolvixOS Dark` (indigo/slate, #6366f1 primary)
   - Call `getTheme` backend function with `project` param

3. **Generate** — Use `anthropics--web-artifacts-builder` skill to compose:
   - Hero section: headline, subheadline, CTA, background gradient
   - Value props: 3-4 cards with icons
   - Features section: detailed feature list with screenshots/mockups
   - Stats bar: key metrics (e.g., block height, TPS, validators)
   - Footer: links, social, copyright

4. **Apply Tokens** — Use theme color_tokens for all colors:
   - `--background`, `--foreground`, `--primary`, `--muted`, `--border`
   - Space Grotesk for headings, Inter for body, JetBrains Mono for numbers
   - 8px spacing scale

5. **Responsive Check** — Verify layout at 375px, 768px, 1024px, 1280px

6. **Accessibility** — Run `auditA11y` backend function

7. **Persist** — Call `generatePage` to create web_artifact record, then `publishArtifact`

## Project Rules
- Verdis landing pages: green accents, blockchain focus, never mention EvolvixOS
- EvolvixOS landing pages: indigo accents, AI engineering focus, never mention blockchain/crypto
- Each project deploys to its own server
