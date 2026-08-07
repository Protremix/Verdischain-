# EvolvixOS Design Directive v2.0

## Scope

This directive governs all web design across the Verdis ecosystem. Two projects share one design language but maintain distinct identities:

- **Verdis Chain** (blockchain) → `verdischain.com` → server `91.98.160.145`
  - Identity: green-black, neon green accents, monospace numerics
  - Primary theme: `Verdis Dark` (primary: #00ff88, background: #040806)
  - Artifacts: blockchain explorer, validator UI, AMM DEX, eco-metrics dashboard

- **EvolvixOS** (AI Engineering OS) → `evolvixos.com` → server `62.238.61.145`
  - Identity: deep slate, indigo/violet accents, engineering-grade UI
  - Primary theme: `EvolvixOS Dark` (primary: #6366f1, background: #0a0e14)
  - Artifacts: platform dashboards, landing page, docs, marketplace, plugin UI

## Core Principles

1. **Dark-first** — All default themes are dark. Light mode is optional, never default.
2. **Premium** — Every surface feels crafted. No default browser styles. No amateur patterns.
3. **Minimalist** — Remove what isn't needed. Whitespace is a feature, not wasted space.
4. **Enterprise-grade** — Consistent, reliable, accessible. Built for professionals.

## Design Tokens

### Spacing Scale (8px base)
`4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px, 64px, 80px`
Never use ad-hoc values (no 7px, 13px, 15px, 22px).

### Typography
- **Headings**: Space Grotesk (500-700)
- **Body**: Inter (300-700)
- **Monospace**: JetBrains Mono (400-700)
- Scale: 12px, 13px, 14px, 15px, 16px, 18px, 20px, 24px, 28px, 32px

### Elevation
- Level 0: Flat (background)
- Level 1: `rgba(0,0,0,0.1)` subtle shadow
- Level 2: `0 4px 24px rgba(0,0,0,0.3)` card shadow
- Level 3: `0 8px 32px rgba(0,0,0,0.4)` modal shadow
- Max elevation: Level 3. Never exceed.

### Border Radius
- sm: 6-8px (inputs, buttons, tags)
- md: 10-12px (cards, panels)
- lg: 14-16px (containers, modals)

### Motion
- Duration: ≤300ms
- Easing: ease-out or cubic-bezier(0.16, 1, 0.3, 1)
- No bouncing, no spring, no excessive animation
- Hover transitions: opacity, transform translateY(-1px), border-color only

## Color Rules

1. ONE accent color per project — never mix Verdis green with EvolvixOS indigo.
2. Semantic colors only: success (green), warning (yellow), error (red).
3. Never use hardcoded hex in React — use CSS variables / Tailwind tokens.
4. Contrast ratio: minimum 4.5:1 for text (WCAG 2.1 AA).
5. Muted text must be readable — minimum 3:1 contrast against background.

## Component Patterns

### Cards
`background: var(--card)`, `border: 1px solid var(--border)`, `backdrop-filter: blur(20px)`, `border-radius: var(--radius)`

### Tables
Data-dense, monospace numerics, hover highlight, no zebra striping. Header in uppercase with letter-spacing.

### Navigation
Sticky, blurred background, brand left, links center, status right. Mobile: collapse to hamburger.

### Stat Cards
Icon (top), value (large gradient text), label (small uppercase muted).

## Responsive Breakpoints
- sm: 640px (mobile landscape)
- md: 768px (tablet)
- lg: 1024px (desktop)
- xl: 1280px (wide)
- 2xl: 1536px (ultra-wide)
Mobile-first: always design for 375px first, then scale up.

## Accessibility (WCAG 2.1 AA)
- Color contrast ≥ 4.5:1 for normal text, ≥ 3:1 for large text
- Focus-visible states on all interactive elements
- Semantic HTML5 landmarks (header, nav, main, footer)
- Alt text on all images
- Keyboard navigation for all interactive elements
- ARIA roles only where semantic HTML is insufficient

## SEO Baseline
- Semantic HTML5 structure
- Meta description on every page
- Open Graph tags (og:type, og:title, og:description, og:image)
- JSON-LD where applicable
- Performant asset loading (preconnect, lazy load images)

## Quality Gates (Mandatory Before Publishing)
1. **Accessibility audit** — 0 P0/P1 issues, score ≥ 90
2. **Consistency check** — matches active theme tokens, score ≥ 90
3. **Responsive check** — works at 375px, 768px, 1024px, 1280px
4. **SEO check** — has meta description, OG tags, semantic structure

## Project Deployment Targets
- **Verdis artifacts** → deploy to `91.98.160.145` under `/opt/verdis-repo/dist/web/`
- **EvolvixOS artifacts** → deploy to `62.238.61.145` under `/opt/evolvixos/frontend-v2/dist/`
- Each artifact must declare its `project` field (verdis | evolvixos)
- Never deploy Verdis designs to the EvolvixOS server or vice versa
