# Working on marin-software

## Architecture

This is a static, zero-build MarinOS app made from marin-app-template. It uses the MarinOS App Shell installed under `vendor/marinos/`; `platform.shell` in `marin.yml` must match `vendor/marinos/manifest.json`.

## Boundaries

- Keep shell component hosts in the initial HTML and load the deferred shell before the app script. Use app-owned templates for the icon, About, and Accessibility content.
- Keep the primary workflow first inside `main#main` as `#start[data-tab-section]`. Do not add duplicate shell section IDs, navigation markup, or a second shell runtime.
- Do not edit `vendor/marinos/`. Use the shell's installer to adopt an approved release, update `platform.shell`, and re-test. Fix shared defects upstream rather than overriding shell internals in app CSS.
- Preserve the app's fonts, security configuration, reporting contacts, and `.nojekyll` unless a separately scoped task changes them. Do not claim a security or accessibility review just because the shell renders those sections.
- Keep the CSP/referrer meta block static and before resource-loading elements. After a reviewed change to `security.json`, run `python3 scripts/sync-security-meta.py --write`; never inject policies at runtime or claim header-only protection via meta tags.

## Before finishing

Run `bash scripts/check.sh` and, when Playwright is available, `bash scripts/check.sh --browser`. Do not claim a security or accessibility review that has not happened.

## References

- `marin-app-shell`: component implementation, integration contract, release notes, and installer.
- `marin-ui`: design system consumed through the shell release, not independently synced into this app.
- `marin-digital-standards`: accessibility, content, brand, security, and product-design requirements.
- `marin-skills/marin-app-builder`: scaffolding workflow that must reflect this component-based starter.
