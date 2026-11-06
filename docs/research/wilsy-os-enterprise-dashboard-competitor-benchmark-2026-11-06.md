# WILSY OS Enterprise Dashboard Competitor Benchmark

**Report:** EOS-UX-01  
**Date:** 2026-11-06  
**Research method:** Primary vendor documentation and standards  
**Purpose:** Extract reusable product and interaction patterns; do not imitate competitor branding.

## Executive finding

Leading enterprise platforms do not treat a dashboard as a wall of metric cards. Their documented patterns combine role-relevant navigation, configurable pages, reusable components, work queues, contextual records and a focused workspace for completing a job.

WILSY should adopt the underlying interaction principles and build a more coherent cross-product operating environment.

## Primary-source benchmark

### SAP Fiori Launchpad

SAP describes spaces as containers for one or more pages, assigned according to user roles. Pages contain apps grouped into sections; administrators select the relevant apps and order sections. The app finder and global search expose eligible apps beyond the curated home page. This is a useful distinction between **what a user is eligible to access** and **what the workspace chooses to feature**.

Source: [SAP Help — Spaces and Pages](https://help.sap.com/docs/btp/sap-fiori-launchpad-for-sap-btp/spaces-and-pages)

WILSY application: EOS issues the eligible module/capability projection; tenant or user workspace preferences may reorder and pin eligible modules, but cannot create eligibility.

### Salesforce Lightning

Salesforce documents app-level configuration for branding, navigation and assigned Lightning pages. Lightning pages are composed from reusable components and can expose tabs and pinned regions for console-style multitasking.

Sources:
- [Salesforce Help — Customize Lightning Apps](https://help.salesforce.com/s/articleView?id=sf.dev_apps_lightning_customize.htm&language=en_US&type=5)
- [Salesforce Help — Lightning Pages](https://help.salesforce.com/s/articleView?id=platform.lightning_page_overview.htm&language=en_US&type=5)
- [Salesforce Help — Add and Customize Tabs](https://help.salesforce.com/s/articleView?id=platform.lightning_app_builder_customize_lex_pages_add_tabs.htm&language=en_US&type=5)

WILSY application: shared shell and reusable workbench components; module-specific pages with stable record context; multiple open records without duplicating data or authority.

### ServiceNow Configurable Workspace

ServiceNow describes a workspace as a focused working area for a job, bringing tasks and workflows together. Documented features include multi-tab work and contextual information to help an operator complete an end-to-end task. UI Builder supports reusable and configurable workspace experiences.

Sources:
- [ServiceNow Docs — UI Builder and Configurable Workspaces](https://www.servicenow.com/docs/r/application-development/ui-builder/ui-builder-csm-workspace.html)
- [ServiceNow Docs — Configuring Configurable Workspace](https://www.servicenow.com/docs/r/platform-user-interface/c_set-up-configurable-workspace.html)

WILSY application: prioritise work queues and task completion over decorative KPI grids; provide a record inspector, history, evidence and next permitted action in one operating room.

### Microsoft Dynamics 365

Dynamics 365 is a suite of role-focused business applications rather than one monolithic screen. Its model-driven application approach is a relevant benchmark for composing navigation, data views and process-oriented experiences. Further Microsoft-specific design research is required before adopting any exact implementation pattern.

Reference starting point: [Microsoft Learn — Dynamics 365 documentation](https://learn.microsoft.com/dynamics365/)

### Odoo

Odoo's application model is relevant to WILSY's modular commercial proposition: businesses can adopt a set of applications and expand their operating footprint over time. The important lesson is modular adoption, not that every module should share one permission or lifecycle.

Reference starting point: [Odoo Documentation](https://www.odoo.com/documentation/)

### Zoho One

Zoho One is a unified suite of business applications. It is a useful packaging benchmark for customers seeking a broad suite, while WILSY must preserve independent product identity and product-level entitlements underneath bundles.

Reference starting point: [Zoho One](https://www.zoho.com/one/)

## Standards and security implications

### NIST SP 800-162 — Attribute-Based Access Control

NIST defines ABAC as evaluating subject, object, requested operation and potentially environmental attributes against policy. This supports WILSY's separation between a module being visible in navigation and a specific operation being authorized for a particular resource.

Source: [NIST SP 800-162](https://csrc.nist.gov/pubs/sp/800/162/upd2/final)

### WCAG 2.2

The W3C WCAG 2.2 Recommendation provides the accessibility baseline for keyboard access, focus, target sizing, contrast and other interaction requirements. The OS shell and every module should be tested against it rather than treating accessibility as a late visual polish pass.

Source: [W3C — Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)

## Cross-competitor design conclusions

1. **Spaces before dashboards:** users need a coherent work context, not a random list of pages.
2. **Role relevance without role inference:** server-issued eligible modules are the ceiling; preferences only curate within that ceiling.
3. **Work is the centre:** queues, records, tasks, approvals, timelines and evidence should dominate the workspace.
4. **Reusable components:** consistent tables, filters, record headers, status provenance, split panes and command actions reduce cognitive load.
5. **Multi-record operations:** tabs or persistent record context are valuable for professional workflows.
6. **Search and app discovery:** global search should find only eligible modules and records visible to the current principal.
7. **Responsive adaptation:** navigation, tables and record inspectors must remain usable on laptop, tablet and mobile.
8. **Honest data states:** live, stale, unavailable, denied, empty and loading are different states. Never replace missing data with invented KPIs.

## WILSY differentiation opportunity

WILSY can unify the above into a single OS experience while keeping independent business products commercially composable. Its differentiation should be:

- one consistent operating shell;
- industry-specific workspaces that are genuinely useful;
- explicit standalone and bundle commercial composition;
- strict separation of commercial entitlements from IAM;
- auditable evidence and source provenance;
- cross-module workflows only where explicit contracts and authorization exist.

## Research limitations

This is a primary-source design-pattern review, not a feature-by-feature competitive teardown or pricing study. No unsupported market-share, performance or superiority claims are made. A second research phase should inspect current product demos and official documentation for Microsoft, Odoo and Zoho in more depth, then test real user tasks against the proposed WILSY workbench.
