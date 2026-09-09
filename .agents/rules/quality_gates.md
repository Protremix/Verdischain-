# Quality Gates

## Mandatory Checks Before Publishing

### 1. Accessibility Audit (WCAG 2.1 AA)
- Color contrast ≥ 4.5:1 for normal text
- Color contrast ≥ 3:1 for large text and UI components
- Focus-visible states on all interactive elements
- Semantic HTML5 landmarks present
- Alt text on all images
- Keyboard navigation works for all interactive elements
- Score ≥ 90 required to pass
- 0 P0 or P1 issues allowed

### 2. Theme Consistency Check
- All colors match active theme tokens (no hardcoded hex)
- Spacing values on 8px scale (4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80)
- Typography uses Space Grotesk / Inter / JetBrains Mono only
- Border radius matches sm/md/lg tokens
- Motion ≤ 300ms with ease-out
- Score ≥ 90 required to pass

### 3. Responsive Check
- Works at 375px (mobile portrait)
- Works at 768px (tablet)
- Works at 1024px (desktop)
- Works at 1280px (wide desktop)
- No horizontal scroll at any breakpoint
- Touch targets ≥ 44px on mobile

### 4. SEO Check
- Has <meta name="description">
- Has Open Graph tags
- Semantic HTML5 structure
- Page title present and descriptive

## Blocking vs Non-Blocking
- P0 (Critical): Blocks publish — must fix before proceeding
- P1 (High): Blocks publish — must fix before proceeding
- P2 (Medium): Non-blocking — logged for follow-up
- P3 (Low): Non-blocking — logged for future improvement

## Failure Handling
1. First failure: Return issues with remediation suggestions
2. Second failure: Escalate to Rojs via notification
3. After fix: Re-run all quality gates before publishing
