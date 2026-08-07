# enforce-theme-consistency

## When to Use
Run on any web_artifact before publishing. Also triggered proactively on draft artifacts.

## Workflow

1. **Load Active Theme** — Fetch the artifact's theme via `getTheme`
2. **Compare Tokens**:
   - **Colors**: Every color in the artifact must match a theme token
     - Check for hardcoded hex values (e.g., `#00ff88` instead of `var(--primary)`)
     - Check for non-token colors in Tailwind classes (e.g., `bg-black` instead of `bg-background`)
   - **Spacing**: All padding/margin/gap values must be on 8px scale
     - Allowed: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80
     - Flag: 7, 13, 15, 22, etc.
   - **Typography**: Font families must be Space Grotesk / Inter / JetBrains Mono
   - **Border Radius**: Must match sm (6-8px), md (10-12px), lg (14-16px)
   - **Motion**: Transitions must be ≤ 300ms with ease-out
   - **Elevation**: Shadows must not exceed Level 3

3. **Project Alignment Check**:
   - Verdis artifacts must use Verdis themes (green primary)
   - EvolvixOS artifacts must use EvolvixOS themes (indigo primary)
   - Shared themes can be used by either project
   - Never mix Verdis green with EvolvixOS indigo in one artifact

4. **Score** — Start at 100, deduct:
   - Wrong project theme: -20
   - Not dark-first without exception: -10
   - Hardcoded colors: -5 per instance (max -20)
   - Off-scale spacing: -5 per instance (max -15)
   - Wrong typography: -5
   - Wrong radius: -3

5. **Create Design Review** — Call `checkConsistency` backend function

6. **Report** — Return consistency score and issues

## Pass Criteria
- Score ≥ 90
- No P0/P1 issues
- Project-theme alignment correct

## Auto-Trigger
This skill runs automatically when a web_artifact status changes to 'draft'.
