## T1
t-472510c8 Add a regression test for login form empty input for EU tenants
t-294b8a12 Add an audit trail to search box
t-4cbb3c1c Add date range filter to plan upgrade behind the proxy
t-57289dae Add saved presets to profile page in read-only mode
t-5d5cafc3 Investigate the race condition in tenant partitioning as part of the gift note for large accounts
t-67c545a4 Kubernetes manifests is ignoring the user's locale
t-97f42e09 Let users pick inline editing from deployment guide
t-de6088d9 Secrets vault is timing out under load (team invites)
t-54dc0a31 Soft deletes is timing out under load behind the proxy
t-1e4956e4 Support a retry button in ranking for admins
t-4c7ebc41 Support undo support in release workflow (dark theme)
t-43ff579d Document toast messages upgrade steps in the legacy view
t-43a1d701 Upgrade reindex job to Postgres 17 for large accounts
t-f3a2e87e Add a regression test for profile page concurrent writes during onboarding
t-83563169 Fix the off-by-one error in shortcut overlay for the Kubernetes migration
t-060f81e8 Support keyboard navigation in result highlighting in the legacy view
t-7edd5d07 Upgrade facet filters to Node 22 for the FX support
t-307b7e0b Cover release workflow permission checks with an e2e test (bulk upload) on first load
t-656b0d96 Add tests for Stripe webhooks permission checks for large accounts
t-972015f3 Document Terraform state limits and quotas during onboarding
t-24451d53 Rate limiter is dropping the last item
t-879404c2 Remove dead code from autocomplete on Safari
t-8eb2a4da Investigate the deadlock in 2FA enrollment on Safari
t-45fdf7d9 Fix TLS certificates sorting dates as strings
t-46b0d33e Add tests for profile page permission checks
t-9998c403 Clean up feature flags in log shipping
t-99476e84 Add a regression test for contributing guide timezone edges
t-7a53d0fb Add a regression test for digest emails happy path behind the proxy
t-494f0820 Add an audit trail to incident runbook for large accounts
t-4211b5a6 Add saved presets to release workflow (offline mode)
t-576b88ab Add tests for TLS certificates permission checks during onboarding
t-c71ae70d Add tests for nightly build timezone edges for the search rewrite behind the proxy
t-fea7c51f Add tests for search box pagination limits
t-f8dd0c51 Add tests for staging environment timezone edges for the accessibility pass
t-db232e76 Add tests for toast messages empty input
t-1ab3df07 Add undo support to settings page for API clients
t-25bc0b35 Audit OAuth callback for privilege escalation for the flag service
t-023ad1a6 Bounce handling is ignoring the user's locale in the export path
t-ab62014c Cache receipt emails results to cut initial load (dark mode)
t-77ddaf40 Clean up feature flags in sidebar
t-32dc7320 Document OAuth callback limits and quotas for the activity history
t-e4421234 Document changelog failure modes behind the proxy
t-45bb7230 Document incident runbook limits and quotas behind the proxy
t-45ce7aad Document staging environment limits and quotas on first load
t-4846e874 Email templates is dropping the last item for the k8s move
t-13890be8 Extract changelog logic into a shared module on first load
t-1be384d6 Fix facet filters failing silently when offline
t-ee86273e Fix orders index hanging on slow networks on first load
t-184cd5bb Fix the memory leak in search indexer for invited users
t-f205ad11 Investigate the layout shift in notification preferences
t-3524d118 Investigate the race condition in schema migrations after login
t-bcde9171 Investigate the stale cache in version header for invited users
t-157eeae4 Let users pick a copy-to-clipboard action from rate limiter for the GDPR export
t-c10d6913 Let users pick dark theme support from result highlighting for admins
t-5b6e9a12 Let users pick dark theme support from synonym dictionary
t-58c0a174 Let users pick inline editing from GraphQL gateway
t-ff73045d Let users pick inline editing from ranking for the free trial
t-cdf9f8b4 Let users pick undo support from API keys
t-c7124234 Refund flow is ignoring the user's locale (data export request) for large accounts
t-49c4171e Remove dead code from autoscaling policy
t-82b2e93d Remove dead code from push notifications in the mobile app
t-94b97e1f Replace the hand-rolled nightly build state machine in read-only mode
t-ef2b8cca Replace the hand-rolled push notifications state machine as part of the perf budget for admins
t-820d31b1 Replace the hand-rolled version header state machine behind the proxy
t-1bbc25e7 Sanitize untrusted input in modal dialog
t-6322ded4 Speed up autocomplete initial load
t-c315ab65 Speed up coverage gate initial load after login
t-6805bb10 Speed up receipt emails cold start
t-e277f645 Split GraphQL gateway into smaller units behind the proxy
t-278ae5c5 Support a dry-run mode in password reset in the mobile app
t-f0f26245 Support dark theme support in autocomplete
t-5c0ddf1d Support keyboard navigation in rate limiter
t-ac3aba76 Support saved presets in refund flow during onboarding
t-98b5f13a Synonym dictionary is breaking after the last deploy
t-d57f518a Write a how-to for GraphQL gateway upgrade steps in read-only mode

## T2
t-43ff579d Document toast messages upgrade steps in the legacy view
t-43a1d701 Upgrade reindex job to Postgres 17 for large accounts
t-f3a2e87e Add a regression test for profile page concurrent writes during onboarding
t-83563169 Fix the off-by-one error in shortcut overlay for the Kubernetes migration
t-060f81e8 Support keyboard navigation in result highlighting in the legacy view
t-16d2570b Rename the payment retries config keys as part of the cluster migration
t-c9033af5 Error responses is ignoring the user's locale
t-355b23ae Profile request validator render time (first-run flow)
t-1d2c0d0d Split date picker into smaller units (SSO rollout)
t-1ee67b67 Add CSRF protection to dependency cache
t-bb3e3460 Fix the duplicate request in profile page as part of the public API v2 for large accounts
t-5ebd2a97 Investigate the memory leak in CORS headers in the legacy view
t-2180f5a4 Typo tolerance is crashing when the list is empty in read-only mode
t-3c0d84ec Add a regression test for error responses concurrent writes
t-44d737dc Add dark theme support to TLS certificates
t-ec24bce9 Fix the null pointer in autocomplete
t-5bde41e2 Fix the null pointer in preview deployments for API clients
t-0ab72579 Add CSRF protection to API keys behind the proxy
t-55da925d Profile shortcut overlay render time
t-2e901bcb Fix push notifications failing silently when offline in the export path
t-885418b1 Fix the race condition in schema migrations
t-135e5356 Add a regression test for release workflow permission checks behind the proxy
t-64384e5c Add date range filter to bounce handling on Safari
t-046c7103 Cache in-app inbox results to cut initial load
t-63d519f4 Write a how-to for test sharding rollback procedure on Safari
t-4584c685 Add a regression test for e2e suite concurrent writes for the onboarding revamp
t-3a59366a Cache Terraform state results to cut p95 latency
t-a065bcd0 Investigate the off-by-one error in session expiry
t-c605357f Split request validator into smaller units after login
t-f1030fa1 Fix the race condition in preview deployments for large accounts
t-390666dd Support date range filter in plan upgrade
t-a1744e66 Split bounce handling into smaller units
t-7b25e87d Speed up read replica memory use for the saved filters on Safari
t-368bfcfe Cover contributing guide permission checks with an e2e test
t-fb1dfb92 Fix error responses dropping the last item
t-6df42a5d Clean up feature flags in onboarding wizard
t-b56757c2 Fix orders index leaking memory on long sessions for large accounts
t-01655360 Support keyboard navigation in invoice PDF
t-e75bf977 Support a progress indicator in payment retries on first load
t-d819ea2b Clean up feature flags in CDN cache on Safari
t-8f0007f8 Cache CDN cache results to cut initial load on Safari
t-ffcb944f Cover email templates empty input with an e2e test
t-071141ce Let users pick a progress indicator from request validator
t-d643a947 Support a retry button in orders index as part of the notification center

## T3
t-472510c8 Add a regression test for login form empty input for EU tenants
t-294b8a12 Add an audit trail to search box
t-57289dae Add saved presets to profile page in read-only mode
t-43ff579d Document toast messages upgrade steps in the legacy view
t-f3a2e87e Add a regression test for profile page concurrent writes during onboarding
t-83563169 Fix the off-by-one error in shortcut overlay for the Kubernetes migration
t-46b0d33e Add tests for profile page permission checks
t-fea7c51f Add tests for search box pagination limits
t-db232e76 Add tests for toast messages empty input
t-1ab3df07 Add undo support to settings page for API clients
t-77ddaf40 Clean up feature flags in sidebar
t-1bbc25e7 Sanitize untrusted input in modal dialog
t-1d2c0d0d Split date picker into smaller units (SSO rollout)
t-bb3e3460 Fix the duplicate request in profile page as part of the public API v2 for large accounts
t-55da925d Profile shortcut overlay render time
t-e7adfadb Remove dead code from modal dialog for large accounts
t-ddfd5708 Fix the off-by-one error in profile page for admins
t-74cf1104 Fix the null pointer in settings page for the webhook idempotency
t-9110de8a Let users pick date range filter from onboarding wizard
t-341b5c34 Add a dry-run mode to chart widget
t-72b4299f Add a regression test for sidebar empty input
t-01cdc3e3 Add tests for data table pagination limits as part of the saved filters
t-08e80022 Add tests for empty states happy path
t-77c88f39 Add tests for toast messages happy path for the search v2
t-4ff8b82c Add undo support to onboarding wizard
t-4fdcef94 Cache login form results to cut cold start in the export path
t-87cde4b2 Cache navigation menu results to cut memory use
t-18ec7708 Clean up feature flags in toast messages
t-8b5eacba Clean up feature flags in toast messages for large accounts
t-8b7f175b Cover date picker concurrent writes with an e2e test for EU tenants
t-bca4470c Cover shortcut overlay retry behaviour with an e2e test
t-c9751f87 Document search box upgrade steps
t-4fd98ae9 Extract toolbar logic into a shared module in the legacy view
t-25640f47 Fix data table timing out under load
t-e711e6ad Fix empty states ignoring the user's locale
t-356c0973 Fix onboarding wizard double-submitting behind the proxy
t-ac584446 Fix profile page crashing when the list is empty (win-back emails) for large accounts
t-0cebb46a Fix shortcut overlay losing state on back navigation for the gift note for EU tenants
t-1a5d9920 Fix the deadlock in chart widget on the free plan
t-6f6d5599 Fix the deadlock in date picker
t-30a3bc00 Fix the memory leak in chart widget
t-7265c768 Fix the null pointer in settings page (gift note)
t-6a9d5265 Fix the race condition in shortcut overlay
t-10ce1430 Investigate the encoding bug in modal dialog (SOC 2 audit) for large accounts
t-51020b7e Investigate the layout shift in login form for the single sign-on launch
t-72e6152d Investigate the layout shift in onboarding wizard for the search v2 for API clients
t-8732deff Investigate the memory leak in sidebar as part of the compliance audit after login
t-1610d2ca Investigate the null pointer in chart widget in read-only mode
t-e763a228 Let users pick a copy-to-clipboard action from profile page
t-455fad06 Let users pick sorting by priority from settings page on Safari
t-89c871b6 Let users pick undo support from chart widget (saved filters)
t-223209ec Let users pick undo support from sidebar in the export path
t-279373f9 Navigation menu is double-submitting
t-d97afa4e Remove dead code from profile page in read-only mode
t-29a3f43e Remove dead code from settings page on first load
t-09c2cf9a Rename the data table config keys for the performance budget
t-7b87c157 Replace the hand-rolled sidebar state machine
t-9b744b4a Replace the hand-rolled toolbar state machine
t-46d1b6ef Rotate the secrets used by onboarding wizard
t-0da62314 Support an audit trail in empty states on Safari
t-a2f9fbf6 Support saved presets in sidebar for API clients
t-1c60ca83 Upgrade modal dialog to Django 5.2
t-7486e257 Upgrade toolbar to Node 22 behind the proxy
t-678af985 Write a how-to for chart widget local setup
t-6df42a5d Clean up feature flags in onboarding wizard
t-dd3c98de Investigate the memory leak in modal dialog behind the proxy
t-ed599bff Split modal dialog into smaller units on first load
t-6d5429d6 Support a progress indicator in chart widget for the vanity domains in the export path
t-6bfed4f1 Upgrade date picker to React 19
t-a6c0992e Extract search box logic into a shared module during onboarding
t-998f5af8 Support inline editing in login form on first load
t-19c292b5 Let users pick a retry button from date picker for EU tenants
t-31e05829 Add a regression test for login form permission checks
t-fcab9c22 Add a regression test for login form timezone edges (SSO rollout) on Safari
t-f5920d5f Add a retry button to profile page
t-0ec2456e Add dark theme support to navigation menu on first load
t-f50dd7d3 Add dark theme support to onboarding wizard behind the proxy
t-adc608c6 Add keyboard navigation to navigation menu
t-ff22988b Add sorting by priority to login form
t-326d70f4 Add tests for login form happy path
t-b3670b05 Clean up feature flags in date picker as part of the CSV import
t-538d8a8c Cover empty states permission checks with an e2e test for API clients
t-57fae455 Date picker is breaking after the last deploy as part of the custom domains for EU tenants
t-5d708c0b Document settings page limits and quotas in the export path
t-93b73c8e Fix chart widget sorting dates as strings (i18n) in the export path
t-3df3810f Fix chart widget timing out under load
t-256839ad Fix the memory leak in chart widget during onboarding
t-c83bc8c0 Fix the memory leak in settings page
t-b517602b Investigate the null pointer in login form (SSO rollout) in the legacy view
t-e05c9f43 Investigate the off-by-one error in toast messages for admins
t-e9fea9e7 Investigate the stale cache in chart widget during onboarding
t-c9664aa6 Let users pick CSV export from empty states
t-4a5c2532 Let users pick sorting by priority from empty states
t-5f308e97 Login form is showing stale data after refresh on the free plan
t-d5e2494f Profile date picker query time on the free plan
t-f94ed9fe Profile page is showing stale data after refresh for the perf budget
t-395f050c Remove dead code from shortcut overlay for the mobile layout on Safari
t-65f0c1c0 Rename the empty states config keys
t-522ef9dd Rotate the secrets used by profile page
t-8f466df6 Sanitize untrusted input in empty states for the working offline for large accounts
t-de4bb662 Shortcut overlay is crashing when the list is empty
t-f452dda2 Speed up data table p95 latency
t-7107639b Speed up modal dialog initial load
t-35fa2e0d Support bulk actions in login form
t-75702f88 Theme switcher is breaking after the last deploy (new invoice layout)
t-6a965142 Toast messages is double-submitting for EU tenants
t-bafda6d9 Upgrade empty states to Python 3.13
t-3ac8eaf6 Upgrade modal dialog to pnpm 10
t-3841b14b Add tests for shortcut overlay timezone edges
t-64c29b4f Support bulk actions in onboarding wizard on the free plan
t-d9d5f0c3 Add a copy-to-clipboard action to sidebar during onboarding
t-a5ca80c8 Add dark theme support to navigation menu
t-da4f8246 Add per-tenant limits to navigation menu
t-7c545795 Cover data table error states with an e2e test for EU tenants
t-f61ab0c9 Document onboarding wizard rollback procedure (feature flags) after login
t-aec56401 Extract toast messages logic into a shared module
t-9ab1379c Fix the memory leak in sidebar
t-a7312379 Remove dead code from chart widget on first load
t-2a8439eb Support dark theme support in chart widget in read-only mode

## T4
t-5d5cafc3 Investigate the race condition in tenant partitioning as part of the gift note for large accounts
t-67c545a4 Kubernetes manifests is ignoring the user's locale
t-de6088d9 Secrets vault is timing out under load (team invites)
t-54dc0a31 Soft deletes is timing out under load behind the proxy
t-83563169 Fix the off-by-one error in shortcut overlay for the Kubernetes migration
t-24451d53 Rate limiter is dropping the last item
t-8eb2a4da Investigate the deadlock in 2FA enrollment on Safari
t-45fdf7d9 Fix TLS certificates sorting dates as strings
t-023ad1a6 Bounce handling is ignoring the user's locale in the export path
t-4846e874 Email templates is dropping the last item for the k8s move
t-1be384d6 Fix facet filters failing silently when offline
t-ee86273e Fix orders index hanging on slow networks on first load
t-184cd5bb Fix the memory leak in search indexer for invited users
t-f205ad11 Investigate the layout shift in notification preferences
t-3524d118 Investigate the race condition in schema migrations after login
t-bcde9171 Investigate the stale cache in version header for invited users
t-c7124234 Refund flow is ignoring the user's locale (data export request) for large accounts
t-98b5f13a Synonym dictionary is breaking after the last deploy
t-c9033af5 Error responses is ignoring the user's locale
t-bb3e3460 Fix the duplicate request in profile page as part of the public API v2 for large accounts
t-5ebd2a97 Investigate the memory leak in CORS headers in the legacy view
t-2180f5a4 Typo tolerance is crashing when the list is empty in read-only mode
t-ec24bce9 Fix the null pointer in autocomplete
t-5bde41e2 Fix the null pointer in preview deployments for API clients
t-2a338400 Investigate the duplicate request in plan upgrade
t-ddfd5708 Fix the off-by-one error in profile page for admins
t-74cf1104 Fix the null pointer in settings page for the webhook idempotency
t-35965319 Investigate the duplicate request in session expiry
t-21da710c Typo tolerance is dropping the last item
t-102a55f3 Investigate the flicker in SMS fallback
t-63a688aa Fix OpenAPI schema losing state on back navigation in the legacy view
t-f01f3d5d Facet filters is returning 500 on invalid input
t-f7c19c08 Fix contributing guide reporting the wrong timezone
t-79c8e18f Fix typo tolerance losing state on back navigation
t-68a6113d Architecture notes is crashing when the list is empty
t-9317e285 Investigate the null pointer in webhook endpoint as part of the offline mode for API clients
t-3949d94c Investigate the flicker in schema migrations
t-0fb462a0 API reference is breaking after the last deploy
t-f68a298b Fix OpenAPI schema breaking after the last deploy (usage-based billing) in the export path
t-71bede00 Fix OpenAPI schema breaking after the last deploy for invited users
t-e0d5c4fa Fix Terraform state crashing when the list is empty (gift note) in the mobile app
t-98e34012 Fix account lockout sorting dates as strings (feature flags)
t-45dd849f Fix bounce handling dropping the last item
t-25640f47 Fix data table timing out under load
t-e711e6ad Fix empty states ignoring the user's locale
t-356c0973 Fix onboarding wizard double-submitting behind the proxy
t-ac584446 Fix profile page crashing when the list is empty (win-back emails) for large accounts
t-5253fe43 Fix ranking failing silently when offline in the export path
t-0cebb46a Fix shortcut overlay losing state on back navigation for the gift note for EU tenants
t-40c20c49 Fix synonym dictionary breaking after the last deploy after login
t-71f61bbc Fix the deadlock in autocomplete
t-1a5d9920 Fix the deadlock in chart widget on the free plan
t-6f6d5599 Fix the deadlock in date picker
t-ff4f4f2f Fix the duplicate request in bounce handling after login
t-b8ae8881 Fix the encoding bug in password reset for large accounts
t-ecbe32dc Fix the layout shift in facet filters for the flag service
t-433dda24 Fix the layout shift in incident runbook for invited users
t-80c746f4 Fix the layout shift in schema migrations behind the proxy
t-c0be9223 Fix the layout shift in secrets vault in the mobile app
t-30a3bc00 Fix the memory leak in chart widget
t-7265c768 Fix the null pointer in settings page (gift note)
t-59608782 Fix the off-by-one error in e2e suite in the legacy view
t-6a9d5265 Fix the race condition in shortcut overlay
t-c54ed773 Fix the stale cache in password reset (data export request)
t-b40dcdc3 Fix the stale cache in read replica (speed budget) in the mobile app
t-3665c4c8 In-app inbox is showing stale data after refresh
t-3d103c33 Investigate the duplicate request in refund flow for large accounts
t-f6d741e3 Investigate the encoding bug in Stripe webhooks
t-10ce1430 Investigate the encoding bug in modal dialog (SOC 2 audit) for large accounts
t-dc05e998 Investigate the flicker in plan upgrade (SAML rollout) in read-only mode
t-58d25a62 Investigate the flicker in receipt emails (SOC 2 audit)
t-51020b7e Investigate the layout shift in login form for the single sign-on launch
t-72e6152d Investigate the layout shift in onboarding wizard for the search v2 for API clients
t-10e4a707 Investigate the memory leak in nightly build
t-3f95288e Investigate the memory leak in nightly build as part of the GDPR export during onboarding
t-526fbb26 Investigate the memory leak in preview deployments during onboarding
t-8732deff Investigate the memory leak in sidebar as part of the compliance audit after login
t-1610d2ca Investigate the null pointer in chart widget in read-only mode
t-596153e8 Investigate the null pointer in synonym dictionary for invited users
t-41a36c86 Investigate the race condition in API reference in the export path
t-fdde83ef Investigate the stale cache in CDN cache
t-8619c4ca Investigate the stale cache in orders index as part of the status page
t-241924b2 Investigate the stale cache in rate limiter for EU tenants
t-a0a7ad12 Lint step is rendering off-screen on small screens in the legacy view
t-279373f9 Navigation menu is double-submitting
t-28b2d28a Soft deletes is failing silently when offline
t-7272cb0b Typo tolerance is hanging on slow networks (offline mode) for large accounts
t-2e901bcb Fix push notifications failing silently when offline in the export path
t-885418b1 Fix the race condition in schema migrations
t-a065bcd0 Investigate the off-by-one error in session expiry
t-f1030fa1 Fix the race condition in preview deployments for large accounts
t-fb1dfb92 Fix error responses dropping the last item
t-b56757c2 Fix orders index leaking memory on long sessions for large accounts
t-1c4ada46 Fix deployment guide sorting dates as strings for the SOC2 controls for admins
t-dd3c98de Investigate the memory leak in modal dialog behind the proxy
t-5b1afc3f Fix the layout shift in email templates for the Kubernetes migration
t-60dfe158 Fix the encoding bug in tax calculation
t-a39dae24 Fix idempotency keys timing out under load
t-5663d537 Usage metering is breaking after the last deploy for the offline mode in read-only mode
t-4a04b51d Investigate the encoding bug in autoscaling policy
t-9db403f0 Investigate the layout shift in architecture notes
t-e74be3fc Investigate the race condition in CORS headers for the feature flags during onboarding
t-c643b84b Autocomplete is rendering off-screen on small screens in the export path
t-a65bdac4 CDN cache is rendering off-screen on small screens
t-cda05227 CORS headers is losing state on back navigation
t-57fae455 Date picker is breaking after the last deploy as part of the custom domains for EU tenants
t-2d1f2ade Error responses is losing state on back navigation
t-c4917c6b Fix SSO login reporting the wrong timezone in the export path
t-795685c6 Fix Terraform state hanging on slow networks for the translations
t-83d74172 Fix account lockout hanging on slow networks
t-4788381e Fix bulk import endpoint showing stale data after refresh
t-93b73c8e Fix chart widget sorting dates as strings (i18n) in the export path
t-3df3810f Fix chart widget timing out under load
t-60c95bfa Fix contributing guide hanging on slow networks (spreadsheet import)
t-318a8a1f Fix magic links leaking memory on long sessions
t-ca3b51e3 Fix nightly build returning 500 on invalid input for admins
t-3b94658f Fix orders index double-submitting
t-017d9ddb Fix push notifications returning 500 on invalid input
t-3f62080d Fix rate limiter showing stale data after refresh
t-ed7f70ea Fix the encoding bug in bulk import endpoint in the legacy view
t-fd0f5894 Fix the encoding bug in lint step
t-a985b2ee Fix the encoding bug in nightly build during onboarding
t-37c9fc4b Fix the flicker in contributing guide on the free plan
t-2019cf13 Fix the layout shift in reindex job
t-256839ad Fix the memory leak in chart widget during onboarding
t-82c387bd Fix the memory leak in notification preferences during onboarding
t-c83bc8c0 Fix the memory leak in settings page
t-29826575 Fix the null pointer in error responses for invited users
t-b279c776 Fix the off-by-one error in typo tolerance
t-bed7d8c7 Fix the race condition in OpenAPI schema
t-f9173d37 Fix the stale cache in soft deletes (throttling) in the legacy view
t-0904ee6a Fix token refresh losing state on back navigation on the free plan
t-9efb27ee Investigate the deadlock in push notifications on the free plan
t-26307d3a Investigate the duplicate request in result highlighting for API clients
t-fce7a674 Investigate the layout shift in error responses
t-985bcfae Investigate the memory leak in version header behind the proxy
t-b517602b Investigate the null pointer in login form (SSO rollout) in the legacy view
t-94526130 Investigate the off-by-one error in staging environment
t-e05c9f43 Investigate the off-by-one error in toast messages for admins
t-2360d80e Investigate the stale cache in Stripe webhooks for large accounts
t-e9fea9e7 Investigate the stale cache in chart widget during onboarding
t-8fa394f2 Investigate the stale cache in pagination
t-5f308e97 Login form is showing stale data after refresh on the free plan
t-4ca4b20d Nightly build is losing state on back navigation for the status page in read-only mode
t-2e176f3e Notification preferences is dropping the last item on Safari
t-669a77a1 Password reset is showing stale data after refresh as part of the free trial in the export path
t-f94ed9fe Profile page is showing stale data after refresh for the perf budget
t-c3991d49 Ranking is reporting the wrong timezone as part of the FX support for invited users
t-d80cf053 Read replica is ignoring the user's locale for the spreadsheet import
t-51cc2bc1 Read replica is returning 500 on invalid input
t-7ae02a45 SSO login is double-submitting on the free plan
t-f86e0144 Schema migrations is sorting dates as strings
t-de4bb662 Shortcut overlay is crashing when the list is empty
t-92ec540a Tenant partitioning is leaking memory on long sessions
t-75702f88 Theme switcher is breaking after the last deploy (new invoice layout)
t-6a965142 Toast messages is double-submitting for EU tenants
t-a5a67f87 Usage metering is showing stale data after refresh for invited users
t-d757ce0b Investigate the layout shift in GraphQL gateway
t-74dfc62d Fix the deadlock in tenant partitioning as part of the Kubernetes migration
t-dc6e6d28 Fix the stale cache in typo tolerance on first load
t-f3184c0e Staging environment is failing silently when offline after login
t-ad0a218e Staging environment is showing stale data after refresh
t-92e1a877 Email templates is dropping the last item
t-4f03ec00 Fix OpenAPI schema showing stale data after refresh
t-1f716a61 Fix lint step dropping the last item after login
t-635e4096 Fix the deadlock in Kubernetes manifests on Safari
t-99fa8fff Fix the layout shift in SMS fallback for admins
t-b5dfec7e Fix the memory leak in GraphQL gateway
t-9ab1379c Fix the memory leak in sidebar
t-7d5b5ab5 Fix the off-by-one error in log shipping
t-6bccebff Fix the race condition in CDN cache for API clients
t-0ca0519a Investigate the layout shift in account lockout
t-0cbd6ebc Investigate the layout shift in plan upgrade
t-69e3b1a2 Investigate the null pointer in role permissions
t-ffcc93a0 Investigate the off-by-one error in digest emails as part of the SSO rollout
t-da0e6e62 Test sharding is leaking memory on long sessions
t-a5eac7a2 Unsubscribe link is hanging on slow networks on first load

## T5
t-83563169 Fix the off-by-one error in shortcut overlay for the Kubernetes migration

## T6
t-67c545a4 Kubernetes manifests is ignoring the user's locale
t-54dc0a31 Soft deletes is timing out under load behind the proxy
t-972015f3 Document Terraform state limits and quotas during onboarding
t-879404c2 Remove dead code from autocomplete on Safari
t-ab62014c Cache receipt emails results to cut initial load (dark mode)
t-f205ad11 Investigate the layout shift in notification preferences
t-58c0a174 Let users pick inline editing from GraphQL gateway
t-ff73045d Let users pick inline editing from ranking for the free trial
t-cdf9f8b4 Let users pick undo support from API keys
t-c315ab65 Speed up coverage gate initial load after login
t-6805bb10 Speed up receipt emails cold start
t-98b5f13a Synonym dictionary is breaking after the last deploy
t-5bde41e2 Fix the null pointer in preview deployments for API clients
t-62c508ac Support inline editing in plan upgrade
t-9110de8a Let users pick date range filter from onboarding wizard
t-5a83966b Cache coverage gate results to cut initial load for large accounts
t-3949d94c Investigate the flicker in schema migrations
t-797ba01b Let users pick CSV export from pagination for large accounts
t-e4f6e93b Add a regression test for plan upgrade happy path for EU tenants
t-2523e5fe Clean up feature flags in changelog on Safari
t-ba59a41e Document in-app inbox upgrade steps
t-18e91605 Extract orders index logic into a shared module for EU tenants
t-356c0973 Fix onboarding wizard double-submitting behind the proxy
t-6f6d5599 Fix the deadlock in date picker
t-30a3bc00 Fix the memory leak in chart widget
t-c54ed773 Fix the stale cache in password reset (data export request)
t-58d25a62 Investigate the flicker in receipt emails (SOC 2 audit)
t-e763a228 Let users pick a copy-to-clipboard action from profile page
t-47f567fc Rename the typo tolerance config keys
t-d96cdf95 Split pagination into smaller units as part of the localisation
t-c605357f Split request validator into smaller units after login
t-6d5429d6 Support a progress indicator in chart widget for the vanity domains in the export path
t-a6c0992e Extract search box logic into a shared module during onboarding
t-7e07996a Add CSV export to password reset in the mobile app
t-31e05829 Add a regression test for login form permission checks
t-1f50b83c Add sorting by priority to API keys
t-ff22988b Add sorting by priority to login form
t-bb8c3682 Add tests for lint step happy path
t-67ce09f8 Cache schema migrations results to cut memory use as part of the CSV import
t-795685c6 Fix Terraform state hanging on slow networks for the translations
t-2019cf13 Fix the layout shift in reindex job
t-f9173d37 Fix the stale cache in soft deletes (throttling) in the legacy view
t-b517602b Investigate the null pointer in login form (SSO rollout) in the legacy view
t-e9fea9e7 Investigate the stale cache in chart widget during onboarding
t-c9664aa6 Let users pick CSV export from empty states
t-a51cea70 Let users pick keyboard navigation from lint step for the GDPR export in the legacy view
t-5f308e97 Login form is showing stale data after refresh on the free plan
t-c469d363 Profile proration query time
t-8f25abf6 Remove dead code from pagination
t-3c6898fe Rename the Kubernetes manifests config keys
t-261813ee Sanitize untrusted input in SSO login as part of the working offline
t-de4bb662 Shortcut overlay is crashing when the list is empty
t-6a965142 Toast messages is double-submitting for EU tenants
t-bafda6d9 Upgrade empty states to Python 3.13
t-3ac8eaf6 Upgrade modal dialog to pnpm 10
t-98430ea3 Write a how-to for pagination limits and quotas
t-ffcb944f Cover email templates empty input with an e2e test
t-64c29b4f Support bulk actions in onboarding wizard on the free plan
t-6a1af860 Cache soft deletes results to cut render time on first load
t-722c49c5 Add an audit trail to contributing guide for the SOC 2 audit for admins
t-da4f8246 Add per-tenant limits to navigation menu
t-ea677125 Document payment retries upgrade steps
t-9f7b9147 Extract SSO login logic into a shared module
t-b5dfec7e Fix the memory leak in GraphQL gateway
t-ffcc93a0 Investigate the off-by-one error in digest emails as part of the SSO rollout
t-28a96155 Replace the hand-rolled idempotency keys state machine

## T7
t-307b7e0b Cover release workflow permission checks with an e2e test (bulk upload) on first load
t-4095864a Add tests for API keys timezone edges (bulk upload)
t-4063c5b2 Cache schema migrations results to cut p95 latency for the bulk upload after login
t-c8fa0a2a Write a how-to for error responses upgrade steps (CSV import) in read-only mode
t-54e07572 Rotate the secrets used by notification preferences (CSV import)
t-67ce09f8 Cache schema migrations results to cut memory use as part of the CSV import
t-b3670b05 Clean up feature flags in date picker as part of the CSV import
t-ebd2c934 Cover orders index happy path with an e2e test for the CSV import for large accounts
t-60c95bfa Fix contributing guide hanging on slow networks (spreadsheet import)
t-d80cf053 Read replica is ignoring the user's locale for the spreadsheet import

## T8
t-b9011686 Add a regression test for preview deployments happy path for the CSV import
t-d4d05a3b Let users pick a retry button from magic links (spreadsheet import) on first load
t-396cf86b Let users pick undo support from connection pool for the spreadsheet import after login
t-b2409a03 Write a how-to for nightly build local setup for the CSV import on first load
t-3ba5698a Split reindex job into smaller units (CSV import) for API clients
t-da48f254 Investigate the stale cache in test sharding for the CSV import for API clients
t-13730e15 Support an audit trail in account lockout as part of the bulk upload on first load
t-4b750314 Fix tenant partitioning losing state on back navigation (bulk upload)
t-8ed4e265 Extract receipt emails logic into a shared module (CSV import)
t-e1a13901 Split receipt emails into smaller units for the spreadsheet import on Safari
t-c300a346 Add a progress indicator to receipt emails (CSV import)
t-f53da490 Upgrade session expiry to Django 5.2 for the bulk upload
t-7ab3dbc3 Add CSRF protection to vacuum schedule as part of the spreadsheet import
t-0c4e4014 Support a dry-run mode in onboarding wizard (CSV import)
t-b720ab78 Investigate the null pointer in API keys
t-9fb8ae38 Let users pick an audit trail from proration as part of the CSV import for large accounts
t-e90917db Investigate the deadlock in data table (spreadsheet import)
t-46606c0d Fix the null pointer in CORS headers as part of the bulk upload
t-45936969 Add a copy-to-clipboard action to search box for the CSV import for EU tenants
t-6a37b3a5 Fix the encoding bug in token refresh (spreadsheet import) for large accounts
t-793a33fe Upgrade role permissions to Node 22 for the spreadsheet import after login
t-31cbdb88 Support an audit trail in toolbar for the spreadsheet import
t-e06badac Write a how-to for push notifications local setup (CSV import)
t-d9a0981b Let users pick CSV export from TLS certificates in read-only mode
t-6aebfd37 Sidebar is losing state on back navigation
t-802dd811 Remove dead code from idempotency keys as part of the CSV import
t-c81932ce Add per-tenant limits to bulk import endpoint for the spreadsheet import during onboarding
t-a7a3e0d3 Add sorting by priority to test sharding (bulk upload)
t-73520984 Let users pick pagination cursors from coverage gate as part of the spreadsheet import in the legacy view
t-acef6227 Write a how-to for refund flow limits and quotas (CSV import) during onboarding
t-c1398762 Fix idempotency keys dropping the last item for the CSV import
t-9d1ffe65 Remove dead code from reindex job as part of the spreadsheet import
t-371fbebe Fix the layout shift in version header (CSV import) on the free plan
t-10543360 Synonym dictionary is sorting dates as strings for the spreadsheet import for EU tenants
t-84d44c7a Profile SMS fallback cold start as part of the CSV import
t-174178bd Support bulk actions in coupon codes
t-5e8d697a Let users pick a progress indicator from Stripe webhooks for the spreadsheet import
t-51bfc2f0 Add CSRF protection to preview deployments as part of the bulk upload behind the proxy
t-736a5cb7 Add date range filter to audit log table as part of the CSV import in the export path
t-a9315496 Fix the stale cache in Kubernetes manifests for the CSV import
t-6230650a Fix Kubernetes manifests hanging on slow networks as part of the bulk upload on the free plan
t-944ec67f Fix the layout shift in version header for the CSV import
t-e3dabd45 Speed up e2e suite initial load as part of the CSV import
t-cf8c6123 Upgrade preview deployments to Node 22 as part of the CSV import
t-8d816076 Support a retry button in test sharding for EU tenants
t-a66247a1 Support CSV export in reindex job for the CSV import
t-a31a14ae Clean up feature flags in invoice PDF (CSV import) on Safari
t-f8c55c00 Speed up payment retries p95 latency as part of the CSV import
t-680332fa Clean up feature flags in rate limiter for the spreadsheet import
t-b43c14b5 Clean up feature flags in 2FA enrollment (spreadsheet import)
t-cc42aaa4 Speed up magic links query time (CSV import) during onboarding
t-744937b6 Let users pick sorting by priority from soft deletes (bulk upload) behind the proxy
t-8e05419a Fix idempotency keys dropping the last item as part of the CSV import
t-046f3680 Add sorting by priority to invoice PDF (CSV import)
t-634c7ab0 Audit contributing guide for privilege escalation as part of the bulk upload after login

## T9
t-43ff579d Document toast messages upgrade steps in the legacy view
t-16d2570b Rename the payment retries config keys as part of the cluster migration
t-c9033af5 Error responses is ignoring the user's locale
t-355b23ae Profile request validator render time (first-run flow)
t-1d2c0d0d Split date picker into smaller units (SSO rollout)
t-1ee67b67 Add CSRF protection to dependency cache
t-bb3e3460 Fix the duplicate request in profile page as part of the public API v2 for large accounts
t-5ebd2a97 Investigate the memory leak in CORS headers in the legacy view
t-2180f5a4 Typo tolerance is crashing when the list is empty in read-only mode
t-3c0d84ec Add a regression test for error responses concurrent writes
t-44d737dc Add dark theme support to TLS certificates
t-ec24bce9 Fix the null pointer in autocomplete
t-5bde41e2 Fix the null pointer in preview deployments for API clients
t-2e901bcb Fix push notifications failing silently when offline in the export path
t-885418b1 Fix the race condition in schema migrations
t-135e5356 Add a regression test for release workflow permission checks behind the proxy
t-64384e5c Add date range filter to bounce handling on Safari
t-046c7103 Cache in-app inbox results to cut initial load
t-63d519f4 Write a how-to for test sharding rollback procedure on Safari
t-4584c685 Add a regression test for e2e suite concurrent writes for the onboarding revamp
t-3a59366a Cache Terraform state results to cut p95 latency
t-a065bcd0 Investigate the off-by-one error in session expiry
t-c605357f Split request validator into smaller units after login
t-f1030fa1 Fix the race condition in preview deployments for large accounts
t-390666dd Support date range filter in plan upgrade
t-e75bf977 Support a progress indicator in payment retries on first load
t-d819ea2b Clean up feature flags in CDN cache on Safari
t-8f0007f8 Cache CDN cache results to cut initial load on Safari
t-ffcb944f Cover email templates empty input with an e2e test
