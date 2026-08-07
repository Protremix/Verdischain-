<!-- build-plan:begin -->
## Active build plan — verdis_design_studio
Work through every step, and confirm each is satisfied before telling the user the agent is ready.

- [ ] Create web_artifact entity to catalog every generated page/component.
- [ ] Create design_review entity to track consistency and accessibility audits.
- [ ] Create theme_profile entity for the 10 EvolvixOS premium themes.
- [ ] Create component_library entity to persist reusable React/shadcn components.
- [ ] Implement backend function `generate_page` — accepts a spec, invokes the web-artifacts-builder skill workflow, returns generated artifact metadata.
- [ ] Implement backend function `generate_dashboard` — accepts a data spec, calls interactive-dashboard-builder, returns Chart.js + React dashboard.
- [ ] Implement backend function `create_penpot_design` — calls the Penpot API (via penpot-uiux-design connector) to create/sync UI/UX design files.
- [ ] Implement backend function `get_theme` — fetches a theme_profile record by id or returns the default dark-first theme.
- [ ] Implement backend function `audit_a11y` — analyzes provided HTML/React for WCAG 2.1 AA compliance and returns issues.
- [ ] Implement backend function `check_design_consistency` — compares an artifact against the EvolvixOS Design Directive and recent artifacts.
- [ ] Implement backend function `publish_artifact` — marks a web_artifact as published and updates its record.
- [ ] Seed theme_profile with the 10 premium theme definitions (dark-first defaults).
- [ ] Write operating rules to .agents/rules/evolvixos_design_directive.md — the core design directive and behavioral guardrails.
- [ ] Write operating rules to .agents/rules/safety_and_scope.md — PII, refusal, and escalation rules.
- [ ] Write operating rules to .agents/rules/quality_gates.md — mandatory checks before publishing artifacts.
- [ ] Create skill: design-landing-page.
- [ ] Create skill: design-dashboard.
- [ ] Create skill: design-explorer-ui.
- [ ] Create skill: audit-accessibility.
- [ ] Create skill: enforce-theme-consistency.
- [ ] Create skill: penpot-sync-design.
- [ ] Create skill: componentize-artifact.
- [ ] Set up in-app channel — available by default to authorized Verdis/EvolvixOS workspace members.
- [ ] Configure Monday 9am cron automation to post the design-inconsistency digest.
- [ ] Configure web_artifact status-change automation to finalize designs.
- [ ] Test end-to-end: generate a landing page, a dashboard, and an explorer UI; verify theming, accessibility, and consistency checks.
<!-- build-plan:end -->