# WILSY OS Workbench Design System

**Report:** EOS-UX-02  
**Date:** 2026-11-06  
**Status:** Target interaction architecture

## Design objective

Replace prototype-style card dashboards with a high-density, calm, professional operating environment. A WILSY workspace should help an operator understand what needs attention, open the relevant record, inspect its evidence and complete an authorised action without hunting through unrelated cards.

## The global application frame

### 1. Persistent OS rail

A compact primary navigation rail provides:
- WILSY OS identity and workspace switcher;
- eligible module navigation grouped by business function;
- global search and command palette;
- favourites and recently visited items;
- notifications and help;
- account, tenant and trust controls.

The rail is not a permission engine. It renders only the current EOS-issued module projection. A hidden module is not necessarily unlicensed, and a visible module does not authorise its APIs.

### 2. Workspace navigation

Within a selected module, use a second-level navigation structure:
- Overview / Command
- Work queue
- Records
- Calendar / deadlines where supported
- Reports
- Configuration where authorised
- Evidence / audit where supported

Only implemented and server-supported destinations should be labelled live. Planned features must not appear as active navigation.

### 3. Context header

Every page should provide a compact title, breadcrumb, current tenant and capacity context, source freshness, last successful refresh and a small number of contextual actions. Avoid oversized hero banners and redundant status cards.

### 4. Workbench canvas

Use task-specific layouts rather than a universal card grid:

- **Queue-first layout:** filterable table/list with priority, owner, status, due date and source.
- **Split-pane layout:** selected row on the left, contextual record inspector on the right.
- **Record operating room:** identity and status header, primary work surface, activity timeline, evidence and related records.
- **Analytics layout:** charts only where a real source and meaningful comparison exist; always expose units, period, freshness and source.
- **Executive layout:** concise financial/operational summaries, decision exceptions, trend context and drill-down. No vanity numbers.

### 5. Action model

Actions appear adjacent to the record and context they affect. Each action must have:
- a clear verb and target;
- an explicit disabled or unavailable explanation;
- confirmation for consequential mutations;
- pending, success, denial and reconciliation states;
- authoritative server readback before the UI claims completion.

The browser never invents workflow transitions, permission or financial authority.

## Visual language

- Neutral, restrained surfaces with strong typographic hierarchy.
- Use WILSY brand accents sparingly for identity, focus and meaningful status.
- Avoid gradients, glowing borders, oversized numbers and repeated decorative cards.
- Dense but readable tables with sticky headers where useful.
- Clear distinction between navigation, data, action and evidence.
- Consistent empty, loading, stale, error and denied states.
- Responsive layouts with no horizontal page overflow.

## Core reusable components

1. OS application shell and module switcher.
2. Workspace navigation and breadcrumb.
3. Search / command palette.
4. Queue table with saved filters and column controls.
5. Record header and contextual inspector.
6. Activity / audit timeline.
7. Evidence viewer and source provenance label.
8. Status badge with semantic state and accessible text.
9. Date / deadline rail.
10. Split-pane and multi-record tab workspace.
11. Decision / approval panel.
12. Chart panel with provenance and period metadata.
13. Empty / unavailable / denied state panel.
14. Responsive navigation drawer.

## Module contract and UI metadata

Each module presentation descriptor should eventually include:
- stable product ID and module ID;
- display label and icon;
- workspace/page manifest;
- route/component mapping;
- supported viewport classes;
- source requirements and source status vocabulary;
- feature/version compatibility;
- required capability identifiers as presentation hints only;
- ownership and support metadata.

The module manifest must come from EOS. The client may map stable module IDs to components but cannot infer entitlement from a role name, local storage, a plan label or a route.

## Legal OS special treatment

Legal OS is a professional workspace, not a generic tenant dashboard. It needs:
- work queue and assigned-work views;
- matter and instruction operating rooms;
- document and process-service workspaces;
- conflict screening/review where separately authorised;
- finance evidence where separately authorised;
- clear confidentiality and G68 posture;
- visible denial when the confidential practice workspace is unavailable.

G68 remains deny-only. Independently authorised projections may remain separately visible, but cannot be combined into an inferred matter workspace or used to bypass denial. Tenant Owner commercial context is separate from professional Legal Practice access.

## Certification requirements

- Keyboard-only navigation and visible focus.
- WCAG 2.2 AA review, including target size, contrast and focus visibility.
- Desktop, tablet and mobile viewport tests.
- Screen-reader labels for navigation, queues, record panels and status changes.
- No fabricated metric or empty-state content.
- Authenticated browser tests for tenant, capacity, module and record boundaries.
- Cross-tenant tests for every data-backed module.
- G68 deny tests proving no protected content leaks through cached UI or navigation.
- Tests for stale, denied, unavailable and partial-source responses.
