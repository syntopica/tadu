## T1

**UI:** Add saved presets to profile page in read-only mode.
**UI:** ASAP: Add an audit trail to search box.
**UI:** Add undo support to settings page for API clients (P1).
**UI:** Clean up feature flags in sidebar.
**UI:** Important: Sanitize untrusted input in modal dialog.
**UI:** URGENT: Add a regression test for login form empty input for EU tenants.
**UI:** Document toast messages upgrade steps in the legacy view (P1).
**Public API:** Support keyboard navigation in rate limiter.
**API:** Let users pick a copy-to-clipboard action from rate limiter for the GDPR export.
**API:** Split GraphQL gateway into smaller units behind the proxy.
**API:** Let users pick undo support from API keys.
**API:** Write a how-to for GraphQL gateway upgrade steps in read-only mode.
**API:** Investigate the stale cache in version header for invited users.
**API:** Let users pick inline editing from GraphQL gateway.
**Search:** Important: Let users pick dark theme support from result highlighting for admins.
**Auth:** Important: Document OAuth callback limits and quotas for the activity history.
**Auth:** Support a dry-run mode in password reset in the mobile app.
**Auth:** Audit OAuth callback for privilege escalation for the flag service (P1).
**Auth:** Investigate the deadlock in 2FA enrollment on Safari.
**Billing:** Support saved presets in refund flow during onboarding (P1).
**CI:** Add saved presets to release workflow (offline mode).
**Billing:** Cache receipt emails results to cut initial load (dark mode).
**Billing:** Important: Speed up receipt emails cold start.
**Search:** Synonym dictionary is breaking after the last deploy.
**Discovery:** Upgrade reindex job to Postgres 17 for large accounts.
**Indexing:** Speed up autocomplete initial load.
**Indexing:** Support dark theme support in autocomplete.
**Search:** Remove dead code from autocomplete on Safari.
**Search:** Support a retry button in ranking for admins.
**Search:** Fix the memory leak in search indexer for invited users.
**Billing:** ASAP: Add date range filter to plan upgrade behind the proxy.
**Search:** Upgrade facet filters to Node 22 for the FX support.
**Notifications:** Bounce handling is ignoring the user's locale in the export path.
**Search:** Support keyboard navigation in result highlighting in the legacy view.
**Notifications:** Add a regression test for digest emails happy path behind the proxy.
**Deploy:** Remove dead code from autoscaling policy.
**Database:** ASAP: Investigate the race condition in tenant partitioning as part of the gift note for large accounts.
**Persistence:** Soft deletes is timing out under load behind the proxy.
**Database:** Fix orders index hanging on slow networks on first load.
**Database:** Investigate the race condition in schema migrations after login.
**Infrastructure:** Secrets vault is timing out under load (team invites).
**Infrastructure:** Fix TLS certificates sorting dates as strings.
**Infrastructure:** Clean up feature flags in log shipping (P1).
**Indexing:** Fix facet filters failing silently when offline.
**Infrastructure:** URGENT: Kubernetes manifests is ignoring the user's locale.
**Infrastructure:** Document staging environment limits and quotas on first load.
**Infrastructure:** Document Terraform state limits and quotas during onboarding.
**Infrastructure:** Add tests for TLS certificates permission checks during onboarding.
**Infrastructure:** Add tests for staging environment timezone edges for the accessibility pass.
**Notifications:** Replace the hand-rolled push notifications state machine as part of the perf budget for admins.
**CI:** Speed up coverage gate initial load after login.
**CI:** Support undo support in release workflow (dark theme).
**CI:** Important: Cover release workflow permission checks with an e2e test (bulk upload) on first load.
**Docs:** Document incident runbook limits and quotas behind the proxy.
**Docs:** Let users pick inline editing from deployment guide.
**Docs:** Add a regression test for contributing guide timezone edges.
**Docs:** Important: Extract changelog logic into a shared module on first load.
**Docs:** Add an audit trail to incident runbook for large accounts (P1).
**Docs:** Document changelog failure modes behind the proxy.

## T2

**CI:** Fix the race condition in preview deployments for large accounts.
**UI:** Fix the off-by-one error in shortcut overlay for the Kubernetes migration.
**UI:** Fix the duplicate request in profile page as part of the public API v2 for large accounts.
**UI:** Clean up feature flags in onboarding wizard.
**UI:** Document toast messages upgrade steps in the legacy view (P1).
**UI:** Add a regression test for profile page concurrent writes during onboarding.
**UI:** Split date picker into smaller units (SSO rollout).
**UI:** Profile shortcut overlay render time.
**API:** Fix error responses dropping the last item.
**API:** Split request validator into smaller units after login.
**API:** Let users pick a progress indicator from request validator (P3).
**API:** Add CSRF protection to API keys behind the proxy.
**API:** Add a regression test for error responses concurrent writes.
**REST API:** Profile request validator render time (first-run flow).
**Public API:** Investigate the memory leak in CORS headers in the legacy view.
**Security:** Investigate the off-by-one error in session expiry (P2).
**Billing:** Rename the payment retries config keys as part of the cluster migration.
**Billing:** Support keyboard navigation in invoice PDF.
**Billing:** Support date range filter in plan upgrade.
**Checkout:** Support a progress indicator in payment retries on first load.
**Discovery:** Fix the null pointer in autocomplete.
**Discovery:** Upgrade reindex job to Postgres 17 for large accounts.
**Search:** Typo tolerance is crashing when the list is empty in read-only mode.
**Alerts:** Fix push notifications failing silently when offline in the export path.
**Search:** Support keyboard navigation in result highlighting in the legacy view.
**Notifications:** Cover email templates empty input with an e2e test (P3).
**Notifications:** Split bounce handling into smaller units.
**Notifications:** Cache in-app inbox results to cut initial load.
**Notifications:** Add date range filter to bounce handling on Safari.
**API:** Error responses is ignoring the user's locale.
**Database:** Speed up read replica memory use for the saved filters on Safari.
**Database:** Fix orders index leaking memory on long sessions for large accounts (P2).
**Database:** Fix the race condition in schema migrations.
**Database:** Support a retry button in orders index as part of the notification center.
**Platform:** Clean up feature flags in CDN cache on Safari (P3).
**Deploy:** Someday: Cache CDN cache results to cut initial load on Safari.
**DevOps:** Cache Terraform state results to cut p95 latency.
**Infrastructure:** Add dark theme support to TLS certificates.
**CI:** Write a how-to for test sharding rollback procedure on Safari.
**CI:** Add a regression test for e2e suite concurrent writes for the onboarding revamp.
**CI:** Add a regression test for release workflow permission checks behind the proxy (P2).
**CI:** Fix the null pointer in preview deployments for API clients.
**CI:** Add CSRF protection to dependency cache.
**Guides:** Cover contributing guide permission checks with an e2e test.

## T3

**UI:** Add saved presets to profile page in read-only mode.
**Frontend:** Fix the null pointer in settings page (gift note).
**UI:** Fix the off-by-one error in profile page for admins.
**UI:** Support an audit trail in empty states on Safari.
**UI:** Add dark theme support to navigation menu on first load.
**UI:** Upgrade date picker to React 19.
**UI:** Let users pick CSV export from empty states.
**UI:** Cover empty states permission checks with an e2e test for API clients.
**UI:** Sanitize untrusted input in empty states for the working offline for large accounts (P2).
**UX:** Fix the memory leak in settings page.
**UI:** Replace the hand-rolled toolbar state machine.
**Web:** Fix onboarding wizard double-submitting behind the proxy.
**UI:** Fix the off-by-one error in shortcut overlay for the Kubernetes migration.
**UI:** Add a regression test for login form permission checks.
**UI:** Support dark theme support in chart widget in read-only mode.
**Dashboard:** Shortcut overlay is crashing when the list is empty (P2).
**Dashboard:** Add tests for toast messages happy path for the search v2.
**UI:** Theme switcher is breaking after the last deploy (new invoice layout).
**UI:** Let users pick a copy-to-clipboard action from profile page.
**UI:** Investigate the stale cache in chart widget during onboarding (P2).
**UI:** ASAP: Add an audit trail to search box.
**UX:** Someday: Add a copy-to-clipboard action to sidebar during onboarding.
**Dashboard:** Cover date picker concurrent writes with an e2e test for EU tenants.
**Web:** Add undo support to onboarding wizard.
**UX:** Upgrade modal dialog to Django 5.2.
**UI:** Remove dead code from chart widget on first load.
**UX:** Profile date picker query time on the free plan (P2).
**UI:** Cache navigation menu results to cut memory use.
**UI:** Fix the deadlock in chart widget on the free plan.
**UI:** Fix shortcut overlay losing state on back navigation for the gift note for EU tenants.
**UI:** Remove dead code from shortcut overlay for the mobile layout on Safari.
**UX:** Investigate the memory leak in modal dialog behind the proxy.
**UX:** Clean up feature flags in toast messages for large accounts.
**UI:** Let users pick sorting by priority from empty states (P2).
**UI:** Replace the hand-rolled sidebar state machine.
**UI:** Fix empty states ignoring the user's locale.
**UI:** Document settings page limits and quotas in the export path.
**UI:** Investigate the null pointer in login form (SSO rollout) in the legacy view (P2).
**UI:** Upgrade toolbar to Node 22 behind the proxy.
**UI:** Fix the duplicate request in profile page as part of the public API v2 for large accounts.
**UX:** Let users pick undo support from sidebar in the export path.
**UI:** Fix the memory leak in chart widget.
**UI:** Add keyboard navigation to navigation menu.
**Frontend:** Investigate the layout shift in onboarding wizard for the search v2 for API clients.
**UI:** Upgrade modal dialog to pnpm 10.
**UI:** Remove dead code from settings page on first load.
**UI:** Investigate the null pointer in chart widget in read-only mode.
**Dashboard:** Add tests for empty states happy path.
**Frontend:** Add a retry button to profile page (P2).
**UI:** Add sorting by priority to login form.
**Web:** Add tests for search box pagination limits.
**UI:** Rename the data table config keys for the performance budget.
**UI:** Clean up feature flags in onboarding wizard.
**UI:** Speed up modal dialog initial load.
**UI:** Navigation menu is double-submitting.
**UI:** Document onboarding wizard rollback procedure (feature flags) after login.
**UI:** Add undo support to settings page for API clients (P1).
**UI:** Clean up feature flags in toast messages.
**UI:** Clean up feature flags in sidebar.
**UI:** Add a regression test for sidebar empty input.
**UI:** Profile page is showing stale data after refresh for the perf budget.
**UI:** Add a dry-run mode to chart widget.
**UI:** Fix data table timing out under load.
**UI:** Add a regression test for login form timezone edges (SSO rollout) on Safari (P2).
**UX:** Fix the memory leak in chart widget during onboarding.
**UI:** Add tests for profile page permission checks.
**Dashboard:** Extract search box logic into a shared module during onboarding.
**UI:** Speed up data table p95 latency.
**UI:** Let users pick date range filter from onboarding wizard.
**UI:** Investigate the off-by-one error in toast messages for admins.
**UI:** Add tests for shortcut overlay timezone edges.
**UI:** Let users pick undo support from chart widget (saved filters).
**UI:** Cover data table error states with an e2e test for EU tenants.
**UI:** Rename the empty states config keys.
**UI:** Support saved presets in sidebar for API clients.
**UI:** Important: Sanitize untrusted input in modal dialog.
**UI:** Rotate the secrets used by profile page.
**UI:** Let users pick a retry button from date picker for EU tenants.
**UI:** Add per-tenant limits to navigation menu.
**UI:** Investigate the layout shift in login form for the single sign-on launch.
**UI:** Toast messages is double-submitting for EU tenants.
**UI:** Clean up feature flags in date picker as part of the CSV import.
**Web:** Extract toolbar logic into a shared module in the legacy view.
**Dashboard:** Write a how-to for chart widget local setup.
**UI:** Add tests for login form happy path.
**Dashboard:** Let users pick sorting by priority from settings page on Safari.
**Web:** Login form is showing stale data after refresh on the free plan (P2).
**UI:** Date picker is breaking after the last deploy as part of the custom domains for EU tenants.
**UI:** URGENT: Add a regression test for login form empty input for EU tenants.
**UI:** Add dark theme support to onboarding wizard behind the proxy.
**UI:** Rotate the secrets used by onboarding wizard.
**UI:** Investigate the encoding bug in modal dialog (SOC 2 audit) for large accounts.
**UX:** Investigate the memory leak in sidebar as part of the compliance audit after login.
**UI:** Document toast messages upgrade steps in the legacy view (P1).
**UI:** Split modal dialog into smaller units on first load.
**UI:** Fix profile page crashing when the list is empty (win-back emails) for large accounts.
**UI:** Fix chart widget timing out under load.
**Web:** Upgrade empty states to Python 3.13.
**UI:** Fix chart widget sorting dates as strings (i18n) in the export path.
**UI:** Add a regression test for profile page concurrent writes during onboarding.
**UX:** Support bulk actions in login form.
**UI:** Split date picker into smaller units (SSO rollout).
**UI:** Add dark theme support to navigation menu.
**UI:** Document search box upgrade steps.
**Frontend:** Cover shortcut overlay retry behaviour with an e2e test.
**UI:** Support inline editing in login form on first load.
**UI:** Profile shortcut overlay render time.
**UI:** Support bulk actions in onboarding wizard on the free plan (P3).
**UI:** Add tests for toast messages empty input.
**UX:** Remove dead code from profile page in read-only mode.
**UI:** Fix the null pointer in settings page for the webhook idempotency.
**UI:** Fix the deadlock in date picker.
**Frontend:** Support a progress indicator in chart widget for the vanity domains in the export path.
**UI:** Remove dead code from modal dialog for large accounts.
**Frontend:** Extract toast messages logic into a shared module.
**UI:** Add tests for data table pagination limits as part of the saved filters.
**UI:** Fix the race condition in shortcut overlay.
**Dashboard:** Fix the memory leak in sidebar (P3).
**UI:** Cache login form results to cut cold start in the export path.

## T4

**Search:** Fix the off-by-one error in typo tolerance.
**Auth:** Fix SSO login reporting the wrong timezone in the export path.
**CI:** Fix the race condition in preview deployments for large accounts.
**Frontend:** Fix the null pointer in settings page (gift note).
**UI:** Fix the off-by-one error in profile page for admins.
**UX:** Fix the memory leak in settings page.
**Web:** Fix onboarding wizard double-submitting behind the proxy.
**UI:** Fix the off-by-one error in shortcut overlay for the Kubernetes migration.
**Dashboard:** Shortcut overlay is crashing when the list is empty (P2).
**UI:** Theme switcher is breaking after the last deploy (new invoice layout).
**UI:** Investigate the stale cache in chart widget during onboarding (P2).
**UI:** Fix the deadlock in chart widget on the free plan.
**UI:** Fix shortcut overlay losing state on back navigation for the gift note for EU tenants.
**UX:** Investigate the memory leak in modal dialog behind the proxy.
**UI:** Fix empty states ignoring the user's locale.
**UI:** Investigate the null pointer in login form (SSO rollout) in the legacy view (P2).
**UI:** Fix the duplicate request in profile page as part of the public API v2 for large accounts.
**UI:** Fix the memory leak in chart widget.
**Search:** Autocomplete is rendering off-screen on small screens in the export path.
**Frontend:** Investigate the layout shift in onboarding wizard for the search v2 for API clients.
**UI:** Investigate the null pointer in chart widget in read-only mode.
**UI:** Navigation menu is double-submitting.
**UI:** Profile page is showing stale data after refresh for the perf budget.
**UI:** Fix data table timing out under load.
**UX:** Fix the memory leak in chart widget during onboarding.
**UI:** Investigate the off-by-one error in toast messages for admins.
**Email:** Fix the memory leak in notification preferences during onboarding.
**Pipeline:** Fix the encoding bug in lint step (P2).
**UI:** Investigate the layout shift in login form for the single sign-on launch.
**UI:** Toast messages is double-submitting for EU tenants.
**Web:** Login form is showing stale data after refresh on the free plan (P2).
**UI:** Date picker is breaking after the last deploy as part of the custom domains for EU tenants.
**UI:** Investigate the encoding bug in modal dialog (SOC 2 audit) for large accounts.
**UX:** Investigate the memory leak in sidebar as part of the compliance audit after login.
**UI:** Fix profile page crashing when the list is empty (win-back emails) for large accounts.
**UI:** Fix chart widget timing out under load.
**UI:** Fix chart widget sorting dates as strings (i18n) in the export path.
**API:** Fix OpenAPI schema breaking after the last deploy for invited users.
**REST API:** Fix idempotency keys timing out under load.
**API:** Investigate the memory leak in version header behind the proxy.
**Endpoints:** Investigate the layout shift in error responses (P2).
**API:** Fix error responses dropping the last item.
**API:** Fix the null pointer in error responses for invited users.
**API:** Investigate the stale cache in pagination.
**API:** Fix OpenAPI schema losing state on back navigation in the legacy view.
**API:** Fix the race condition in OpenAPI schema.
**API:** Investigate the stale cache in rate limiter for EU tenants.
**API:** Fix the memory leak in GraphQL gateway.
**Public API:** Investigate the null pointer in webhook endpoint as part of the offline mode for API clients.
**Public API:** Fix OpenAPI schema breaking after the last deploy (usage-based billing) in the export path.
**Endpoints:** Fix bulk import endpoint showing stale data after refresh.
**API:** Fix rate limiter showing stale data after refresh (P2).
**API:** Investigate the layout shift in GraphQL gateway.
**API:** Investigate the race condition in CORS headers for the feature flags during onboarding.
**Public API:** Investigate the memory leak in CORS headers in the legacy view.
**API:** Fix OpenAPI schema showing stale data after refresh.
**Endpoints:** Error responses is losing state on back navigation.
**API:** Investigate the stale cache in version header for invited users.
**API:** CORS headers is losing state on back navigation.
**API:** Rate limiter is dropping the last item.
**API:** Fix the encoding bug in bulk import endpoint in the legacy view.
**Pipeline:** Fix the off-by-one error in e2e suite in the legacy view.
**Database:** Fix the stale cache in soft deletes (throttling) in the legacy view.
**Auth:** Fix token refresh losing state on back navigation on the free plan.
**Identity:** Investigate the null pointer in role permissions.
**Auth:** SSO login is double-submitting on the free plan.
**Auth:** Fix account lockout hanging on slow networks (P2).
**Auth:** Fix the encoding bug in password reset for large accounts.
**Auth:** Fix magic links leaking memory on long sessions.
**Login:** Investigate the layout shift in account lockout.
**Auth:** Password reset is showing stale data after refresh as part of the free trial in the export path.
**Security:** Investigate the off-by-one error in session expiry (P2).
**Identity:** Fix the stale cache in password reset (data export request).
**Auth:** Investigate the deadlock in 2FA enrollment on Safari.
**Pipeline:** Fix lint step dropping the last item after login.
**Billing:** Investigate the encoding bug in Stripe webhooks.
**Docs:** Fix deployment guide sorting dates as strings for the SOC2 controls for admins.
**Auth:** Fix account lockout sorting dates as strings (feature flags).
**Billing:** Refund flow is ignoring the user's locale (data export request) for large accounts.
**Billing:** Investigate the layout shift in plan upgrade.
**Subscriptions:** Investigate the stale cache in Stripe webhooks for large accounts (P2).
**Billing:** Fix the encoding bug in tax calculation.
**Search:** Synonym dictionary is breaking after the last deploy.
**Discovery:** Fix the stale cache in typo tolerance on first load.
**Indexing:** Typo tolerance is dropping the last item.
**Discovery:** Fix the null pointer in autocomplete.
**Search:** Fix typo tolerance losing state on back navigation.
**Search:** Fix synonym dictionary breaking after the last deploy after login.
**Search:** Facet filters is returning 500 on invalid input.
**UI:** Fix the null pointer in settings page for the webhook idempotency.
**Search:** Ranking is reporting the wrong timezone as part of the FX support for invited users.
**Indexing:** Fix the deadlock in autocomplete.
**Search:** Fix the memory leak in search indexer for invited users.
**Search:** Investigate the null pointer in synonym dictionary for invited users.
**Search:** Typo tolerance is hanging on slow networks (offline mode) for large accounts.
**Search:** Typo tolerance is crashing when the list is empty in read-only mode.
**Search:** Fix the layout shift in facet filters for the flag service.
**Search:** Fix ranking failing silently when offline in the export path.
**Notifications:** Fix the duplicate request in bounce handling after login.
**Notifications:** Investigate the off-by-one error in digest emails as part of the SSO rollout.
**Alerts:** Fix push notifications failing silently when offline in the export path.
**Notifications:** Bounce handling is ignoring the user's locale in the export path.
**Messaging:** Fix push notifications returning 500 on invalid input.
**Billing:** Usage metering is showing stale data after refresh for invited users (P2).
**Notifications:** Fix the layout shift in SMS fallback for admins.
**Notifications:** In-app inbox is showing stale data after refresh.
**Notifications:** Notification preferences is dropping the last item on Safari.
**Notifications:** Investigate the deadlock in push notifications on the free plan.
**Notifications:** Email templates is dropping the last item for the k8s move.
**Notifications:** Fix bounce handling dropping the last item.
**Messaging:** Fix the layout shift in email templates for the Kubernetes migration.
**Notifications:** Someday: Email templates is dropping the last item.
**Notifications:** Someday: Unsubscribe link is hanging on slow networks on first load.
**Database:** Tenant partitioning is leaking memory on long sessions.
**Database:** ASAP: Investigate the race condition in tenant partitioning as part of the gift note for large accounts.
**Database:** Soft deletes is failing silently when offline.
**UI:** Fix the deadlock in date picker.
**Database:** Read replica is ignoring the user's locale for the spreadsheet import.
**API:** Error responses is ignoring the user's locale.
**Persistence:** Soft deletes is timing out under load behind the proxy.
**Storage:** Investigate the stale cache in orders index as part of the status page.
**Database:** Fix orders index hanging on slow networks on first load.
**Database:** Fix orders index leaking memory on long sessions for large accounts (P2).
**Database:** Fix the race condition in schema migrations.
**Database:** Investigate the race condition in schema migrations after login.
**DB:** Fix orders index double-submitting (P2).
**Database:** Fix the stale cache in read replica (speed budget) in the mobile app.
**Database:** Schema migrations is sorting dates as strings.
**DB:** Fix the deadlock in tenant partitioning as part of the Kubernetes migration.
**Database:** Fix the layout shift in schema migrations behind the proxy.
**Infrastructure:** Secrets vault is timing out under load (team invites).
**Infrastructure:** Fix TLS certificates sorting dates as strings.
**Database:** Read replica is returning 500 on invalid input.
**Infrastructure:** Someday: Fix the deadlock in Kubernetes manifests on Safari.
**Infrastructure:** Investigate the stale cache in CDN cache.
**Infra:** Investigate the off-by-one error in staging environment.
**Infrastructure:** Fix the layout shift in secrets vault in the mobile app.
**Indexing:** Fix facet filters failing silently when offline.
**Infrastructure:** Fix the off-by-one error in log shipping.
**Infrastructure:** URGENT: Kubernetes manifests is ignoring the user's locale.
**Platform:** Fix the race condition in CDN cache for API clients.
**Infrastructure:** Staging environment is showing stale data after refresh.
**Infrastructure:** Fix Terraform state hanging on slow networks for the translations.
**Infrastructure:** Investigate the encoding bug in autoscaling policy.
**Infrastructure:** Fix Terraform state crashing when the list is empty (gift note) in the mobile app.
**Platform:** Staging environment is failing silently when offline after login (P3).
**Indexing:** Fix the layout shift in reindex job.
**Infrastructure:** CDN cache is rendering off-screen on small screens.
**CI:** Investigate the memory leak in preview deployments during onboarding.
**CI:** Investigate the memory leak in nightly build.
**CI:** Test sharding is leaking memory on long sessions (P3).
**Tests:** Investigate the memory leak in nightly build as part of the GDPR export during onboarding.
**CI:** Fix nightly build returning 500 on invalid input for admins.
**CI:** Fix the null pointer in preview deployments for API clients.
**Tests:** Lint step is rendering off-screen on small screens in the legacy view.
**UI:** Fix the race condition in shortcut overlay.
**CI:** Fix the encoding bug in nightly build during onboarding.
**Build:** Nightly build is losing state on back navigation for the status page in read-only mode.
**Docs:** Investigate the race condition in API reference in the export path.
**Dashboard:** Fix the memory leak in sidebar (P3).
**Guides:** Architecture notes is crashing when the list is empty.
**README:** Fix contributing guide reporting the wrong timezone.
**Docs:** API reference is breaking after the last deploy.
**Messaging:** Investigate the layout shift in notification preferences.
**Docs:** Fix the flicker in contributing guide on the free plan.
**Docs:** Fix the layout shift in incident runbook for invited users.
**Billing:** Usage metering is breaking after the last deploy for the offline mode in read-only mode.
**Docs:** Investigate the layout shift in architecture notes.
**README:** Fix contributing guide hanging on slow networks (spreadsheet import).

## T5

none

## T6

**UI:** Let users pick CSV export from empty states.
**Web:** Fix onboarding wizard double-submitting behind the proxy.
**UI:** Add a regression test for login form permission checks.
**Dashboard:** Shortcut overlay is crashing when the list is empty (P2).
**UI:** Let users pick a copy-to-clipboard action from profile page.
**UI:** Investigate the stale cache in chart widget during onboarding (P2).
**UI:** Investigate the null pointer in login form (SSO rollout) in the legacy view (P2).
**UI:** Fix the memory leak in chart widget.
**UI:** Upgrade modal dialog to pnpm 10.
**UI:** Add sorting by priority to login form.
**Dashboard:** Extract search box logic into a shared module during onboarding.
**UI:** Let users pick date range filter from onboarding wizard.
**UI:** Add per-tenant limits to navigation menu.
**UI:** Toast messages is double-submitting for EU tenants.
**Web:** Login form is showing stale data after refresh on the free plan (P2).
**Web:** Upgrade empty states to Python 3.13.
**UI:** Support bulk actions in onboarding wizard on the free plan (P3).
**API:** Replace the hand-rolled idempotency keys state machine.
**API:** Split request validator into smaller units after login.
**API:** Add sorting by priority to API keys.
**API:** Fix the memory leak in GraphQL gateway.
**API:** Split pagination into smaller units as part of the localisation.
**API:** Let users pick CSV export from pagination for large accounts.
**Endpoints:** Remove dead code from pagination.
**API:** Let users pick undo support from API keys.
**API:** Write a how-to for pagination limits and quotas.
**API:** Let users pick inline editing from GraphQL gateway.
**Database:** Fix the stale cache in soft deletes (throttling) in the legacy view.
**Identity:** Sanitize untrusted input in SSO login as part of the working offline.
**Identity:** Fix the stale cache in password reset (data export request).
**Database:** Investigate the flicker in schema migrations.
**Auth:** Extract SSO login logic into a shared module.
**Billing:** Document payment retries upgrade steps.
**Billing:** Profile proration query time.
**Checkout:** Add a regression test for plan upgrade happy path for EU tenants.
**Billing:** Cache receipt emails results to cut initial load (dark mode).
**Billing:** Support inline editing in plan upgrade.
**Payments:** Investigate the flicker in receipt emails (SOC 2 audit).
**Billing:** Important: Speed up receipt emails cold start.
**Search:** Synonym dictionary is breaking after the last deploy.
**Search:** Let users pick inline editing from ranking for the free trial.
**Search:** Remove dead code from autocomplete on Safari.
**Search:** Rename the typo tolerance config keys.
**Notifications:** Investigate the off-by-one error in digest emails as part of the SSO rollout.
**Notifications:** Cover email templates empty input with an e2e test (P3).
**Notifications:** Document in-app inbox upgrade steps.
**UI:** Fix the deadlock in date picker.
**Database:** Extract orders index logic into a shared module for EU tenants.
**Persistence:** Soft deletes is timing out under load behind the proxy.
**Database:** Cache soft deletes results to cut render time on first load.
**Database:** Cache schema migrations results to cut memory use as part of the CSV import.
**Frontend:** Support a progress indicator in chart widget for the vanity domains in the export path.
**Infrastructure:** Rename the Kubernetes manifests config keys.
**Infrastructure:** URGENT: Kubernetes manifests is ignoring the user's locale.
**Infrastructure:** Document Terraform state limits and quotas during onboarding.
**Infrastructure:** Fix Terraform state hanging on slow networks for the translations.
**Indexing:** Fix the layout shift in reindex job.
**CI:** Cache coverage gate results to cut initial load for large accounts.
**CI:** Speed up coverage gate initial load after login.
**CI:** Fix the null pointer in preview deployments for API clients.
**CI:** Let users pick keyboard navigation from lint step for the GDPR export in the legacy view (P2).
**Build:** Add tests for lint step happy path.
**Documentation:** Add an audit trail to contributing guide for the SOC 2 audit for admins (P3).
**Messaging:** Investigate the layout shift in notification preferences.
**Auth:** Add CSV export to password reset in the mobile app.
**Docs:** Clean up feature flags in changelog on Safari.

## T7

**UI:** Clean up feature flags in date picker as part of the CSV import.
**API:** Write a how-to for error responses upgrade steps (CSV import) in read-only mode.
**Email:** Rotate the secrets used by notification preferences (CSV import).
**Database:** Read replica is ignoring the user's locale for the spreadsheet import.
**Persistence:** Cover orders index happy path with an e2e test for the CSV import for large accounts.
**Database:** Cache schema migrations results to cut memory use as part of the CSV import.
**README:** Fix contributing guide hanging on slow networks (spreadsheet import).

## T8

2026-11-05 — **CI:** Add a regression test for preview deployments happy path for the CSV import.
2026-10-29 — **Auth:** Let users pick a retry button from magic links (spreadsheet import) on first load.
2026-10-03 — **CI:** Write a how-to for nightly build local setup for the CSV import on first load.
2026-09-18 — **Discovery:** Split reindex job into smaller units (CSV import) for API clients.
2026-09-06 — **Build:** Investigate the stale cache in test sharding for the CSV import for API clients.
2026-08-19 — **Billing:** Extract receipt emails logic into a shared module (CSV import).
2026-08-06 — **Checkout:** Split receipt emails into smaller units for the spreadsheet import on Safari.
2026-08-04 — **Billing:** Add a progress indicator to receipt emails (CSV import).
2026-07-10 — **Database:** Add CSRF protection to vacuum schedule as part of the spreadsheet import.
2026-07-09 — **UI:** Support a dry-run mode in onboarding wizard (CSV import).
2026-06-08 — **Billing:** Let users pick an audit trail from proration as part of the CSV import for large accounts.
2026-04-29 — **UI:** Add a copy-to-clipboard action to search box for the CSV import for EU tenants.
2026-04-01 — **Auth:** Fix the encoding bug in token refresh (spreadsheet import) for large accounts.
2026-03-28 — **Auth:** Upgrade role permissions to Node 22 for the spreadsheet import after login.
2026-03-20 — **UI:** Support an audit trail in toolbar for the spreadsheet import.
2026-02-22 — **API:** Remove dead code from idempotency keys as part of the CSV import.
2026-02-14 — **REST API:** Add per-tenant limits to bulk import endpoint for the spreadsheet import during onboarding.
2026-02-09 — **CI:** Let users pick pagination cursors from coverage gate as part of the spreadsheet import in the legacy view.
2026-02-01 — **Billing:** Write a how-to for refund flow limits and quotas (CSV import) during onboarding.
2026-01-27 — **API:** Fix idempotency keys dropping the last item for the CSV import.
2026-01-23 — **Search:** Remove dead code from reindex job as part of the spreadsheet import.
2026-01-15 — **API:** Fix the layout shift in version header (CSV import) on the free plan.
2026-01-05 — **Indexing:** Synonym dictionary is sorting dates as strings for the spreadsheet import for EU tenants.
2025-12-28 — **Notifications:** Profile SMS fallback cold start as part of the CSV import.
2025-12-19 — **Checkout:** Let users pick a progress indicator from Stripe webhooks for the spreadsheet import.
2025-12-12 — **Database:** Add date range filter to audit log table as part of the CSV import in the export path.
2025-12-11 — **Infrastructure:** Fix the stale cache in Kubernetes manifests for the CSV import.
2025-12-03 — **API:** Fix the layout shift in version header for the CSV import.
2025-11-15 — **CI:** Upgrade preview deployments to Node 22 as part of the CSV import.
2025-09-29 — **Search:** Support CSV export in reindex job for the CSV import.
2025-09-13 — **Payments:** Clean up feature flags in invoice PDF (CSV import) on Safari.
2025-08-08 — **Billing:** Speed up payment retries p95 latency as part of the CSV import.
2025-08-07 — **API:** Clean up feature flags in rate limiter for the spreadsheet import.
2025-07-30 — **Auth:** Clean up feature flags in 2FA enrollment (spreadsheet import).
2025-07-03 — **API:** Fix idempotency keys dropping the last item as part of the CSV import.
2025-06-03 — **Checkout:** Add sorting by priority to invoice PDF (CSV import).

## T9

**CI:** Fix the race condition in preview deployments for large accounts.
**UI:** Fix the duplicate request in profile page as part of the public API v2 for large accounts.
**UI:** Document toast messages upgrade steps in the legacy view (P1).
**UI:** Split date picker into smaller units (SSO rollout).
**API:** Split request validator into smaller units after login.
**API:** Add a regression test for error responses concurrent writes.
**REST API:** Profile request validator render time (first-run flow).
**Public API:** Investigate the memory leak in CORS headers in the legacy view.
**Security:** Investigate the off-by-one error in session expiry (P2).
**Billing:** Rename the payment retries config keys as part of the cluster migration.
**Billing:** Support date range filter in plan upgrade.
**Checkout:** Support a progress indicator in payment retries on first load.
**Discovery:** Fix the null pointer in autocomplete.
**Search:** Typo tolerance is crashing when the list is empty in read-only mode.
**Alerts:** Fix push notifications failing silently when offline in the export path.
**Notifications:** Cover email templates empty input with an e2e test (P3).
**Notifications:** Cache in-app inbox results to cut initial load.
**Notifications:** Add date range filter to bounce handling on Safari.
**API:** Error responses is ignoring the user's locale.
**Database:** Fix the race condition in schema migrations.
**Platform:** Clean up feature flags in CDN cache on Safari (P3).
**Deploy:** Someday: Cache CDN cache results to cut initial load on Safari.
**DevOps:** Cache Terraform state results to cut p95 latency.
**Infrastructure:** Add dark theme support to TLS certificates.
**CI:** Write a how-to for test sharding rollback procedure on Safari.
**CI:** Add a regression test for e2e suite concurrent writes for the onboarding revamp.
**CI:** Add a regression test for release workflow permission checks behind the proxy (P2).
**CI:** Fix the null pointer in preview deployments for API clients.
**CI:** Add CSRF protection to dependency cache.
