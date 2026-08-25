# WILSY OS - PRODUCTION REPOSITORY FILE MAP
Generated on: Sat Jul 25 08:22:57 UTC 2026

## Directory Structure
```
.
├── .babelrc
├── .env
├── .env.example
├── .env.production
├── .env.staging
├── .eslintrc.json
├── .mocharc.cjs
├── .npmrc
├── .nvmrc
├── .vscode
│   ├── settings.json
│   └── tailwind.json
├── PROJECT_FILE_MAP.md
├── debug-login.sh
├── diagnose-css.sh
├── fix-all-imports.sh
├── fix-eslint.sh
├── fix-proptypes.sh
├── fix_tests.js
├── forensic-audit.sh
├── generate_map.sh
├── index.html
├── package-lock.json
├── package.json
├── postcss.config.js
├── public
│   ├── assets
│   │   └── images
│   │       └── superadmin
│   │           ├── wilsy-logo.svg
│   │           └── wilsy.jpeg
│   └── favicon.ico
├── run-tests.sh
├── src
│   ├── App.jsx
│   ├── api
│   │   └── axiosConfig.js
│   ├── assets
│   │   ├── iconManifest.js
│   │   ├── icons
│   │   │   ├── client-covenant-board.svg
│   │   │   ├── crisis-command.svg
│   │   │   ├── forensic-vault.svg
│   │   │   ├── global-orchestrator.svg
│   │   │   ├── node-registry.svg
│   │   │   ├── revenue-ledger.svg
│   │   │   ├── risk-sentinel.svg
│   │   │   └── sovereign-identity-hub.svg
│   │   └── logo
│   │       ├── wilsy-icon.svg
│   │       ├── wilsy-logo.svg
│   │       ├── wilsy.jpeg
│   │       └── wilsy.pdf
│   ├── components
│   │   ├── ComplianceHUD.jsx
│   │   ├── ComplianceHUD.module.css
│   │   ├── ErrorBoundary.jsx
│   │   ├── ForensicsHUD.css
│   │   ├── ForensicsHUD.jsx
│   │   ├── ForensicsHUD.module.css
│   │   ├── HUDAlertBanner.jsx
│   │   ├── RevenueHUD.jsx
│   │   ├── RevenueHUD.module.css
│   │   ├── Security.jsx
│   │   ├── SingularityDashboard.css
│   │   ├── SingularityDashboard.jsx
│   │   ├── SingularityToggle.jsx
│   │   ├── SingularityToggle.module.css
│   │   ├── SovereignContractGenerator.jsx
│   │   ├── SovereignHub.jsx
│   │   ├── StatCard.jsx
│   │   ├── account
│   │   │   ├── WilsyAccountCommandCenter.jsx
│   │   │   ├── wilsyAccountChromeRuntimeCss.js
│   │   │   ├── wilsyAccountCommandRouteContracts.js
│   │   │   ├── wilsyAccountRuntimeEnhancers.js
│   │   │   ├── wilsyAccountThemeTokens.js
│   │   │   ├── wilsyNebulaCommandSkin.js
│   │   │   └── wilsyOperatingSkins.js
│   │   ├── ai_ethics
│   │   │   └── AIEthicsDashboard.jsx
│   │   ├── analytics
│   │   │   ├── AnalyticsDashboard.jsx
│   │   │   ├── InvestorKPIs.jsx
│   │   │   ├── QuantumForecasts.jsx
│   │   │   └── UserActivity.jsx
│   │   ├── artifacts
│   │   │   ├── BusinessArtifactStudio.jsx
│   │   │   └── BusinessArtifactStudio.module.css
│   │   ├── auth
│   │   │   ├── CovenantPortal.jsx
│   │   │   ├── CovenantPortal.module.css
│   │   │   ├── SovereignLogin.jsx
│   │   │   ├── SovereignMfaPortal.jsx
│   │   │   ├── Sovereign_Signature_Pad.jsx
│   │   │   ├── Sovereign_Signature_Pad.module.css
│   │   │   └── WelcomePortal.jsx
│   │   ├── billing
│   │   │   ├── BillingHUD.jsx
│   │   │   ├── BillingHUD.module.css
│   │   │   └── InvoiceSentinel.jsx
│   │   ├── chrome
│   │   │   ├── WilsyChromePrimitives.jsx
│   │   │   ├── WilsyForensicMerkleShowroom.jsx
│   │   │   └── WilsyForensicMerkleShowroom.module.css
│   │   ├── compliance
│   │   │   └── ComplianceDashboard.jsx
│   │   ├── control-room
│   │   │   ├── ExecutiveControlRoom.jsx
│   │   │   └── ExecutiveControlRoom.module.css
│   │   ├── coo
│   │   │   └── COODashboard.jsx
│   │   ├── crm
│   │   │   ├── CRMDashboard.jsx
│   │   │   ├── CRMDashboard.jsx.bak.r72f-controlled-cockpit-wire-20260625-074756
│   │   │   ├── CRMDashboard.jsx.bak.r72f1-controlled-cockpit-wire-rescue-20260625-075020
│   │   │   ├── CRMDashboard.jsx.bak.r91k105b-20260629-175125
│   │   │   ├── CRMDashboard.jsx.bak.r91k109-20260629-181715
│   │   │   ├── CRMDashboard.jsx.bak.r91k110-20260629-182353
│   │   │   ├── CRMDashboard.jsx.bak.r91k110b-20260629-182510
│   │   │   ├── CRMDashboard.jsx.bak.r91k111-20260629-183134
│   │   │   ├── CRMDashboard.jsx.bak.r91k114-20260629-185608
│   │   │   ├── CRMDashboard.jsx.bak.r91k114b-20260629-185814
│   │   │   ├── CRMDashboard.jsx.bak.r91k117b-20260629-195501
│   │   │   ├── CRMDashboard.jsx.bak.r91k117c-20260629-195906
│   │   │   ├── CRMDashboard.jsx.bak.r91k117d-20260629-200957
│   │   │   ├── CRMDashboard.jsx.bak.r91k118a-20260629-202026
│   │   │   ├── CRMDashboard.jsx.bak.r91k118b-20260629-202248
│   │   │   ├── CRMDashboard.jsx.bak.r91k119a-before-route-20260629-202943
│   │   │   ├── CRMDashboard.jsx.bak.r91k120c-20260629-204219
│   │   │   ├── CRMDashboard.jsx.bak.r91k121a-20260629-204641
│   │   │   ├── CRMDashboard.jsx.bak.r91k122a-screen-death-20260629-205422
│   │   │   ├── CRMDashboard.jsx.bak.r91k123b-20260629-210812
│   │   │   ├── CRMDashboard.jsx.bak.r91k124a-20260629-211538
│   │   │   ├── CRMDashboard.jsx.bak.r91k131-20260629-224835
│   │   │   ├── CRMDashboard.jsx.bak.r91k131b-20260629-225418
│   │   │   ├── CRMDashboard.jsx.bak.r91k131c-docguard-20260629-225636
│   │   │   ├── CRMDashboard.jsx.bak.r91k131d-docguard-final-20260629-225826
│   │   │   ├── CRMDashboard.jsx.bak.r91k132a-css-module-binding-20260629-230125
│   │   │   ├── CRMDashboard.jsx.bak.r91k133a-hierarchy-20260629-230536
│   │   │   ├── CRMDashboard.jsx.bak.r91k133b-continuation-20260629-230754
│   │   │   ├── CRMDashboard.jsx.bak.r91k139a-source-signature-fabric-20260629-234118
│   │   │   ├── CRMDashboard.jsx.bak.r91k143a-fabric-backend-contract-20260629-235642
│   │   │   ├── CRMDashboard.jsx.bak.r91k145a-live-fabric-contained-ui-20260630-002344
│   │   │   ├── CRMDashboard.jsx.bak.r91k146a-live-contract-sync-20260630-003520
│   │   │   ├── CRMDashboard.jsx.bak.r91k147a-sourceguide-state-bridge-20260630-004230
│   │   │   ├── CRMDashboard.jsx.bak.r91k147b-marker-rescue-20260630-004629
│   │   │   ├── CRMDashboard.jsx.bak.r91k147c-sourceguide-assignment-bridge-20260630-004952
│   │   │   ├── CRMDashboard.jsx.bak.r91k148a-fetch-contract-bridge-20260630-005612
│   │   │   ├── CRMDashboard.jsx.bak.r91k148b-fetch-return-ast-rescue-20260630-010215
│   │   │   ├── CRMDashboard.jsx.bak.r91k149a-force-sourceguide-fetch-20260630-010716
│   │   │   ├── CRMDashboard.jsx.bak.r91k150a-render-model-contract-override-20260630-012551
│   │   │   ├── CRMDashboard.jsx.bak.r91k150b-bad-literal-rescue-20260630-012807
│   │   │   ├── CRMDashboard.jsx.bak.r91k151b-proof-root-fabric-typography-20260630-013624
│   │   │   ├── CRMDashboard.jsx.bak.r91k153a-fabric-command-identity-20260630-034902
│   │   │   ├── CRMDashboard.jsx.bak.r91k153b-anchor-safe-fabric-command-identity-20260630-035137
│   │   │   ├── CRMDashboard.jsx.bak.r91k154a-lean-fabric-command-identity-20260630-035904
│   │   │   ├── CRMDashboard.jsx.bak.r91k154b-current-contract-lean-fabric-20260630-040808
│   │   │   ├── CRMDashboard.jsx.bak.r91k155a-fabric-live-posture-typography-20260630-041427
│   │   │   ├── CRMDashboard.jsx.bak.r91k157a-create-path-to-100-20260630-044920
│   │   │   ├── CRMDashboard.jsx.bak.r91k157b-anchor-safe-create-path-to-100-20260630-045527
│   │   │   ├── CRMDashboard.jsx.bak.r91k157b-anchor-safe-create-path-to-100-20260630-045622
│   │   │   ├── CRMDashboard.jsx.bak.r91k157c-broken-before-syntax-restore-20260630-045920
│   │   │   ├── CRMDashboard.jsx.bak.r91k157d-create-early-return-20260630-050444
│   │   │   ├── CRMDashboard.jsx.bak.r91k157e-useeffect-import-rescue-20260630-050703
│   │   │   ├── CRMDashboard.jsx.bak.r91k157f-create-fetch-docguard-20260630-050824
│   │   │   ├── CRMDashboard.jsx.bak.r91k158a-live-create-command-board-20260630-051503
│   │   │   ├── CRMDashboard.jsx.bak.r91k158b-findgate-docguard-20260630-051630
│   │   │   ├── CRMDashboard.jsx.bak.r91k159a-live-create-button-backend-wiring-20260630-052608
│   │   │   ├── CRMDashboard.jsx.bak.r91k159c-visible-live-receipt-hud-20260630-055938
│   │   │   ├── CRMDashboard.jsx.bak.r91k159d-receipt-hud-token-rescue-20260630-060205
│   │   │   ├── CRMDashboard.jsx.bak.r91k160a-create-ui-containment-20260630-061757
│   │   │   ├── CRMDashboard.jsx.bak.r91k160a-create-ui-containment-20260630-062725
│   │   │   ├── CRMDashboard.jsx.bak.r91k161a-create-operating-workbench-20260630-063339
│   │   │   ├── CRMDashboard.jsx.bak.r91k161a-create-operating-workbench-20260630-063954
│   │   │   ├── CRMDashboard.jsx.bak.r91k162a-create-command-containment-20260630-064415
│   │   │   ├── CRMDashboard.jsx.bak.r91k162b-flexible-command-map-rescue-20260630-064738
│   │   │   ├── CRMDashboard.jsx.bak.r91k162c-broken-before-restore-20260630-065040
│   │   │   ├── CRMDashboard.jsx.bak.r91k162d-broken-before-restore-20260630-065223
│   │   │   ├── CRMDashboard.jsx.bak.r91k163a-source-activation-os-20260630-070136
│   │   │   ├── CRMDashboard.jsx.bak.r91k164a-current-before-stability-restore-20260630-070702
│   │   │   ├── CRMDashboard.jsx.bak.r91k166a-wilsy-ai-cockpit-20260630-073535
│   │   │   ├── CRMDashboard.jsx.bak.r91k169a-live-signal-strip-jsx-only-20260630-080122
│   │   │   ├── CRMDashboard.jsx.bak.r91k170a-source-list-menu-operating-shell-20260630-082110
│   │   │   ├── CRMDashboard.jsx.bak.r91k170a-source-list-menu-operating-shell-20260630-082406
│   │   │   ├── CRMDashboard.jsx.bak.r91k170b-wrapper-before-no-selftrip-20260630-082405
│   │   │   ├── CRMDashboard.jsx.bak.r91k171a-enhance-wilsy-ai-rail-only-20260630-083949
│   │   │   ├── CRMDashboard.jsx.bak.r91k172a-finalise-daily-forensic-drawers-20260630-085043
│   │   │   ├── CRMDashboard.jsx.bak.r91k174a-critical-connector-need-20260630-091835
│   │   │   ├── CRMDashboard.jsx.bak.r91k175d-jsx-dead-helper-data-contract-squash-20260630-094033
│   │   │   ├── CRMDashboard.module.css
│   │   │   ├── CRMDashboard.module.css.bak.r91k104-20260629-171445
│   │   │   ├── CRMDashboard.module.css.bak.r91k104b-20260629-171613
│   │   │   ├── CRMDashboard.module.css.bak.r91k104b-20260629-173123
│   │   │   ├── CRMDashboard.module.css.bak.r91k105b-20260629-175125
│   │   │   ├── CRMDashboard.module.css.bak.r91k106-20260629-175836
│   │   │   ├── CRMDashboard.module.css.bak.r91k106r-20260629-180235
│   │   │   ├── CRMDashboard.module.css.bak.r91k107-20260629-180544
│   │   │   ├── CRMDashboard.module.css.bak.r91k107r-20260629-181132
│   │   │   ├── CRMDashboard.module.css.bak.r91k117b-20260629-195501
│   │   │   ├── CRMDashboard.module.css.bak.r91k117c-20260629-195906
│   │   │   ├── CRMDashboard.module.css.bak.r91k118a-20260629-202026
│   │   │   ├── CRMDashboard.module.css.bak.r91k119a-before-route-20260629-202943
│   │   │   ├── CRMDashboard.module.css.bak.r91k121a-20260629-204641
│   │   │   ├── CRMDashboard.module.css.bak.r91k122a-screen-death-20260629-205422
│   │   │   ├── CRMDashboard.module.css.bak.r91k123b-20260629-210812
│   │   │   ├── CRMDashboard.module.css.bak.r91k124a-20260629-211538
│   │   │   ├── CRMDashboard.module.css.bak.r91k124b-20260629-212758
│   │   │   ├── CRMDashboard.module.css.bak.r91k124c-20260629-213407
│   │   │   ├── CRMDashboard.module.css.bak.r91k125b-20260629-214533
│   │   │   ├── CRMDashboard.module.css.bak.r91k125c-20260629-215002
│   │   │   ├── CRMDashboard.module.css.bak.r91k125c-20260629-215139
│   │   │   ├── CRMDashboard.module.css.bak.r91k127a-20260629-220636
│   │   │   ├── CRMDashboard.module.css.bak.r91k128a-20260629-221011
│   │   │   ├── CRMDashboard.module.css.bak.r91k129a-20260629-221727
│   │   │   ├── CRMDashboard.module.css.bak.r91k129b-20260629-222206
│   │   │   ├── CRMDashboard.module.css.bak.r91k130a-remove-broken-ledger-20260629-222559
│   │   │   ├── CRMDashboard.module.css.bak.r91k131-20260629-224835
│   │   │   ├── CRMDashboard.module.css.bak.r91k131b-20260629-225418
│   │   │   ├── CRMDashboard.module.css.bak.r91k132a-css-module-binding-20260629-230125
│   │   │   ├── CRMDashboard.module.css.bak.r91k133a-hierarchy-20260629-230536
│   │   │   ├── CRMDashboard.module.css.bak.r91k133b-continuation-20260629-230754
│   │   │   ├── CRMDashboard.module.css.bak.r91k134a-final-composition-20260629-231132
│   │   │   ├── CRMDashboard.module.css.bak.r91k135a-active-stage-motion-20260629-231621
│   │   │   ├── CRMDashboard.module.css.bak.r91k136a-active-stage-bleed-seal-20260629-232125
│   │   │   ├── CRMDashboard.module.css.bak.r91k137a-active-stage-command-bar-20260629-232854
│   │   │   ├── CRMDashboard.module.css.bak.r91k138a-row-contract-20260629-233401
│   │   │   ├── CRMDashboard.module.css.bak.r91k139a-source-signature-fabric-20260629-234118
│   │   │   ├── CRMDashboard.module.css.bak.r91k140a-fabric-no-overlap-20260629-234535
│   │   │   ├── CRMDashboard.module.css.bak.r91k141a-fabric-action-clearance-20260629-234817
│   │   │   ├── CRMDashboard.module.css.bak.r91k142a-fabric-header-typography-20260629-235141
│   │   │   ├── CRMDashboard.module.css.bak.r91k145a-live-fabric-contained-ui-20260630-002344
│   │   │   ├── CRMDashboard.module.css.bak.r91k146a-live-contract-sync-20260630-003520
│   │   │   ├── CRMDashboard.module.css.bak.r91k147a-sourceguide-state-bridge-20260630-004230
│   │   │   ├── CRMDashboard.module.css.bak.r91k147b-marker-rescue-20260630-004629
│   │   │   ├── CRMDashboard.module.css.bak.r91k151b-proof-root-fabric-typography-20260630-013624
│   │   │   ├── CRMDashboard.module.css.bak.r91k152a-fabric-command-composition-20260630-034115
│   │   │   ├── CRMDashboard.module.css.bak.r91k153a-fabric-command-identity-20260630-034902
│   │   │   ├── CRMDashboard.module.css.bak.r91k153b-anchor-safe-fabric-command-identity-20260630-035137
│   │   │   ├── CRMDashboard.module.css.bak.r91k154a-lean-fabric-command-identity-20260630-035904
│   │   │   ├── CRMDashboard.module.css.bak.r91k154b-current-contract-lean-fabric-20260630-040808
│   │   │   ├── CRMDashboard.module.css.bak.r91k155a-fabric-live-posture-typography-20260630-041427
│   │   │   ├── CRMDashboard.module.css.bak.r91k157a-create-path-to-100-20260630-044920
│   │   │   ├── CRMDashboard.module.css.bak.r91k157b-anchor-safe-create-path-to-100-20260630-045527
│   │   │   ├── CRMDashboard.module.css.bak.r91k157b-anchor-safe-create-path-to-100-20260630-045622
│   │   │   ├── CRMDashboard.module.css.bak.r91k157d-create-early-return-20260630-050444
│   │   │   ├── CRMDashboard.module.css.bak.r91k158a-live-create-command-board-20260630-051503
│   │   │   ├── CRMDashboard.module.css.bak.r91k159a-live-create-button-backend-wiring-20260630-052608
│   │   │   ├── CRMDashboard.module.css.bak.r91k159c-visible-live-receipt-hud-20260630-055938
│   │   │   ├── CRMDashboard.module.css.bak.r91k159d-receipt-hud-token-rescue-20260630-060205
│   │   │   ├── CRMDashboard.module.css.bak.r91k160a-create-ui-containment-20260630-061757
│   │   │   ├── CRMDashboard.module.css.bak.r91k160a-create-ui-containment-20260630-062725
│   │   │   ├── CRMDashboard.module.css.bak.r91k161a-create-operating-workbench-20260630-063339
│   │   │   ├── CRMDashboard.module.css.bak.r91k161a-create-operating-workbench-20260630-063954
│   │   │   ├── CRMDashboard.module.css.bak.r91k162a-create-command-containment-20260630-064415
│   │   │   ├── CRMDashboard.module.css.bak.r91k162b-flexible-command-map-rescue-20260630-064738
│   │   │   ├── CRMDashboard.module.css.bak.r91k162c-css-before-restore-20260630-065040
│   │   │   ├── CRMDashboard.module.css.bak.r91k162d-css-before-restore-20260630-065223
│   │   │   ├── CRMDashboard.module.css.bak.r91k163a-source-activation-os-20260630-070136
│   │   │   ├── CRMDashboard.module.css.bak.r91k164a-current-before-stability-restore-20260630-070702
│   │   │   ├── CRMDashboard.module.css.bak.r91k166a-wilsy-ai-cockpit-20260630-073535
│   │   │   ├── CRMDashboard.module.css.bak.r91k167a-cockpit-bleed-containment-20260630-074036
│   │   │   ├── CRMDashboard.module.css.bak.r91k168a-collapsible-progressive-disclosure-20260630-075107
│   │   │   ├── CRMDashboard.module.css.bak.r91k170a-source-list-menu-operating-shell-20260630-082110
│   │   │   ├── CRMDashboard.module.css.bak.r91k170a-source-list-menu-operating-shell-20260630-082406
│   │   │   ├── CRMDashboard.module.css.bak.r91k170b-wrapper-before-no-selftrip-20260630-082405
│   │   │   ├── CRMDashboard.module.css.bak.r91k171a-enhance-wilsy-ai-rail-only-20260630-083949
│   │   │   ├── CRMDashboard.module.css.bak.r91k172a-finalise-daily-forensic-drawers-20260630-085043
│   │   │   ├── CRMDashboard.module.css.bak.r91k173a-source-menu-command-list-20260630-090142
│   │   │   ├── CRMDashboard.module.css.bak.r91k174a-critical-connector-need-20260630-091835
│   │   │   ├── CRMDashboard.module.css.bak.r91k175b-css-obsolete-block-squash-20260630-093227
│   │   │   ├── CrmSearchOutcomeRuntime.js
│   │   │   ├── SovereignCRMClient.jsx
│   │   │   ├── TerminalEvidenceCockpitPanel.js
│   │   │   ├── WilsyCrmRawStreamThread.jsx
│   │   │   ├── account
│   │   │   │   ├── WilsyAccountOperatingRoom.jsx
│   │   │   │   └── WilsyAccountOperatingRoom.module.css
│   │   │   ├── contact
│   │   │   │   ├── WilsyContactOperatingRoom.jsx
│   │   │   │   └── WilsyContactOperatingRoom.module.css
│   │   │   ├── lead
│   │   │   │   ├── WilsyLeadCommandCapsule.js
│   │   │   │   ├── WilsyLeadCustomViewBuilder.jsx
│   │   │   │   ├── WilsyLeadEditSurface.js
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.20260706-082557
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.20260706-084615
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k102-20260629-163503
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k102b-20260629-163957
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k102c-20260629-164112
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k102d-20260629-164332
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k102e-20260629-164504
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k102f-20260629-164750
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k85-20260629-134002
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k85b-20260629-134209
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k87-20260629-135557
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k88-20260629-140657
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k88b-20260629-140850
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k91-20260629-141854
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k91b-20260629-142028
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k92-20260629-142435
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.bak.r91k94-20260629-143309
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.before-eof-cleanup.bak.20260706-082924
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.before-fg41-rescue.bak.20260706-084758
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.before-fg42-context-header.bak.20260706-090650
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.before-fg42-safe-header.bak.20260706-091039
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.before-sort-button-syntax-fix.bak.20260706-084942
│   │   │   │   ├── WilsyLeadOperatingRoom.jsx.failed-fg39.bak.20260706-082807
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.bak.20260706-082557
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.bak.20260706-084615
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.bak.r91k102-20260629-163503
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.bak.r91k102b-20260629-163957
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.bak.r91k85-20260629-134002
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.bak.r91k85b-20260629-134209
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.bak.r91k87-20260629-135557
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.before-eof-cleanup.bak.20260706-082924
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.before-fg41-rescue.bak.20260706-084758
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.before-fg42-context-header.bak.20260706-090650
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.before-fg42-css-context-header.bak.20260706-091322
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.before-fg42-safe-header.bak.20260706-091039
│   │   │   │   ├── WilsyLeadOperatingRoom.module.css.before-sort-button-syntax-fix.bak.20260706-084942
│   │   │   │   └── WilsyLeadOperatingRoom.module.css.failed-fg39.bak.20260706-082807
│   │   │   ├── meeting
│   │   │   │   ├── WilsyMeetingOperatingRoom.jsx
│   │   │   │   ├── WilsyMeetingOperatingRoom.module.css
│   │   │   │   ├── WilsyMeetingRecordsIntelligencePanel.jsx
│   │   │   │   ├── WilsyUniversalMeetingCommandCenter.jsx
│   │   │   │   ├── WilsyUniversalMeetingCommandCenter.module.css
│   │   │   │   ├── index.js
│   │   │   │   └── workspace
│   │   │   │       ├── WilsyMeetingCapsuleView.jsx
│   │   │   │       ├── WilsyMeetingEditor.jsx
│   │   │   │       ├── WilsyMeetingEvidenceWorkspace.jsx
│   │   │   │       ├── WilsyMeetingImportWorkspace.jsx
│   │   │   │       ├── WilsyMeetingParticipantResolver.jsx
│   │   │   │       ├── WilsyMeetingsOverview.jsx
│   │   │   │       ├── WilsyMeetingsWorkspace.jsx
│   │   │   │       ├── WilsyMeetingsWorkspace.module.css
│   │   │   │       └── index.js
│   │   │   ├── rail
│   │   │   │   ├── CrmSovereignSideRail.jsx
│   │   │   │   └── CrmSovereignSideRail.module.css
│   │   │   ├── setup
│   │   │   │   ├── WilsyCrmSetupControlPlane.jsx
│   │   │   │   └── WilsyCrmSetupControlPlane.module.css
│   │   │   └── theme
│   │   │       └── wilsyCrmThemeEngineBridge.js
│   │   ├── customer_success
│   │   │   └── CustomerSuccessDashboard.jsx
│   │   ├── data
│   │   │   └── DataDashboard.jsx
│   │   ├── engineering
│   │   │   └── EngineeringDashboard.jsx
│   │   ├── executive
│   │   │   ├── ExecutiveDashboard.jsx
│   │   │   └── ExecutiveDashboard.module.css
│   │   ├── finance
│   │   │   └── FinanceDashboard.jsx
│   │   ├── forms
│   │   │   └── TenantOnboarding.jsx
│   │   ├── hr
│   │   │   └── HrDashboard.jsx
│   │   ├── industry
│   │   │   ├── AgricultureDashboard.jsx
│   │   │   ├── ConsultingDashboard.jsx
│   │   │   ├── EducationDashboard.jsx
│   │   │   ├── EnergyDashboard.jsx
│   │   │   ├── EntertainmentDashboard.jsx
│   │   │   ├── FinanceDashboard.jsx
│   │   │   ├── HealthcareDashboard.jsx
│   │   │   ├── HospitalityDashboard.jsx
│   │   │   ├── LegalDashboard.jsx
│   │   │   ├── LogisticsDashboard.jsx
│   │   │   ├── NonprofitDashboard.jsx
│   │   │   ├── ProductionDashboard.jsx
│   │   │   ├── ProjectDashboard.jsx
│   │   │   ├── PropertyDashboard.jsx
│   │   │   ├── PublicDashboard.jsx
│   │   │   ├── RetailDashboard.jsx
│   │   │   ├── SportsDashboard.jsx
│   │   │   └── TechDashboard.jsx
│   │   ├── intelligence
│   │   │   ├── WilsyOSExecutionCanvas.jsx
│   │   │   ├── WilsyOSIntelligenceDock.jsx
│   │   │   ├── WilsyOSIntelligenceDock.module.css
│   │   │   ├── WilsyOSIntelligenceDockRuntime.jsx
│   │   │   ├── WilsyOSIntelligenceGlobalRuntime.jsx
│   │   │   ├── WilsyOSIntelligenceLauncher.jsx
│   │   │   ├── WilsyOSIntelligenceLauncher.module.css
│   │   │   ├── wilsyAIConversationHistoryEngine.js
│   │   │   ├── wilsyAIDynamicSuggestionEngine.js
│   │   │   └── wilsyOperatorIntelligenceEngine.js
│   │   ├── it
│   │   │   └── ITDashboard.jsx
│   │   ├── knowledge
│   │   │   ├── WilsyKnowledgeBaseVault.jsx
│   │   │   ├── WilsyKnowledgeBaseVault.module.css
│   │   │   ├── WilsyKnowledgeBaseVault.module.module.css.fg108-before-final-receipt
│   │   │   └── operating
│   │   │       ├── KnowledgeOperatingBar.jsx
│   │   │       └── KnowledgeOperatingBar.module.css
│   │   ├── legal
│   │   │   └── LegalDashboard.jsx
│   │   ├── longevity_sciences
│   │   │   └── LongevityDashboard.jsx
│   │   ├── marketing
│   │   │   └── MarketingDashboard.jsx
│   │   ├── operating-console
│   │   │   ├── ExecutiveOperatingConsole.jsx
│   │   │   └── index.js
│   │   ├── operations
│   │   │   └── OperationsDashboard.jsx
│   │   ├── os
│   │   │   ├── WilsyOSDashboardChrome.jsx
│   │   │   ├── WilsyOSDashboardChrome.module.css
│   │   │   ├── WilsyOSDashboardTopRail.jsx
│   │   │   └── wilsyDashboardChromeConfig.js
│   │   ├── procurement
│   │   │   └── ProcurementDashboard.jsx
│   │   ├── product
│   │   │   └── ProductDashboard.jsx
│   │   ├── quantum_computing
│   │   │   └── QuantumDashboard.jsx
│   │   ├── research
│   │   │   └── ResearchDashboard.jsx
│   │   ├── sales
│   │   │   ├── AISalesIntelligenceDashboard.jsx
│   │   │   ├── SalesDashboard.jsx
│   │   │   └── SalesRepresentativeDashboard.jsx
│   │   ├── security
│   │   │   └── SecurityDashboard.jsx
│   │   ├── sovereign
│   │   │   ├── AuditEntry.jsx
│   │   │   ├── AuditEntry.module.css
│   │   │   ├── AuditModule.jsx
│   │   │   ├── AuditModule.module.css
│   │   │   ├── AuditTimeline.jsx
│   │   │   ├── AuditTimeline.module.css
│   │   │   ├── Audit_Vault_Security.jsx
│   │   │   ├── BatchVerificationView.jsx
│   │   │   ├── BatchVerificationView.module.css
│   │   │   ├── BoardroomHUD.jsx
│   │   │   ├── BoardroomHUD.module.css
│   │   │   ├── CloudUplinkDashboard.jsx
│   │   │   ├── CommandPalette.jsx
│   │   │   ├── CommandPalette.module.css
│   │   │   ├── ComplianceDashboard.jsx
│   │   │   ├── ComplianceDashboard.module.css
│   │   │   ├── CoverPage.jsx
│   │   │   ├── DataOrchestrator.jsx
│   │   │   ├── DemoIgnitionButton.jsx
│   │   │   ├── Document_Vault_Interface.jsx
│   │   │   ├── Document_Vault_Interface.module.css
│   │   │   ├── ForensicsDashboard.jsx
│   │   │   ├── ForensicsDashboard.module.css
│   │   │   ├── FounderDashboard.jsx
│   │   │   ├── FounderDashboard.module.css
│   │   │   ├── GeneralDashboard.jsx
│   │   │   ├── InvestorIntelligencePortal.jsx
│   │   │   ├── MetricCard.jsx
│   │   │   ├── MetricCard.module.css
│   │   │   ├── NeuralNarrativeCapsule.jsx
│   │   │   ├── NeuralNarrativeCapsule.module.css
│   │   │   ├── NucleusFeedMonitor.jsx
│   │   │   ├── NucleusFeedMonitor.module.css
│   │   │   ├── QuickPanel.jsx
│   │   │   ├── QuickPanel.module.css
│   │   │   ├── RevenueDashboard.jsx
│   │   │   ├── RevenueDashboard.module.css
│   │   │   ├── RiskSentinel.jsx
│   │   │   ├── RiskSentinel.module.css
│   │   │   ├── SecurityManager.jsx
│   │   │   ├── SovereignDashboardController.jsx
│   │   │   ├── SovereignHub.jsx
│   │   │   ├── SovereignHub.module.css
│   │   │   ├── SovereignLogin.jsx
│   │   │   ├── SovereignNodeDashboard.jsx
│   │   │   ├── SovereignNodeDashboard.module.css
│   │   │   ├── SovereignOrchestrator.jsx
│   │   │   ├── SovereignSidebar.css
│   │   │   ├── SovereignSidebar.jsx
│   │   │   ├── SovereignSidebar.module.css
│   │   │   ├── Sovereign_Audit_Vault.jsx
│   │   │   ├── Sovereign_Audit_Vault.module.css
│   │   │   ├── Sovereign_Client_Covenant.jsx
│   │   │   ├── Sovereign_Cloud_Gateway.jsx
│   │   │   ├── Sovereign_Covenant.module.css
│   │   │   ├── Sovereign_Covenant_Modal.jsx
│   │   │   ├── Sovereign_Crisis_Command.jsx
│   │   │   ├── Sovereign_Crisis_Command.module.css
│   │   │   ├── Sovereign_Document_Vault.jsx
│   │   │   ├── Sovereign_Forensic_Exporter.jsx
│   │   │   ├── Sovereign_Global_Topography.jsx
│   │   │   ├── Sovereign_Global_Topography.module.css
│   │   │   ├── Sovereign_Identity_Auth.jsx
│   │   │   ├── Sovereign_Identity_Auth.module.css
│   │   │   ├── Sovereign_Identity_Hub.jsx
│   │   │   ├── Sovereign_Identity_Hub.module.css
│   │   │   ├── Sovereign_Legal_Analytics.jsx
│   │   │   ├── Sovereign_Node_Registry.jsx
│   │   │   ├── Sovereign_Node_Registry.module.css
│   │   │   ├── Sovereign_Onboarding_Wizard.jsx
│   │   │   ├── Sovereign_Revenue_Ledger.jsx
│   │   │   ├── Sovereign_Revenue_Ledger.module.css
│   │   │   ├── Sovereign_StatementEngine.jsx
│   │   │   ├── Sovereign_StatementEngine.module.css
│   │   │   ├── Sovereign_TenantManager.jsx
│   │   │   ├── Sovereign_TenantManager.module.css
│   │   │   ├── Sovereign_User_Management.jsx
│   │   │   ├── TenantDevTool.jsx
│   │   │   ├── TenantDiscovery.jsx
│   │   │   ├── TenantDiscovery.module.css
│   │   │   ├── TenantManagementGrid.jsx
│   │   │   ├── TenantManagementGrid.module.css
│   │   │   ├── TenantSwitcher.jsx
│   │   │   ├── TenantSwitcher.module.css
│   │   │   └── WilsyGlobalCommandSearch.jsx
│   │   ├── space_operations
│   │   │   └── SpaceOperationsDashboard.jsx
│   │   ├── superadmin
│   │   │   └── layout
│   │   │       ├── Header.jsx
│   │   │       ├── Header.module.css
│   │   │       ├── Layout.module.css
│   │   │       ├── Sidebar.jsx
│   │   │       ├── Sidebar.module.css
│   │   │       └── SuperAdminLayout.jsx
│   │   ├── technical
│   │   │   └── TechnicalDashboard.jsx
│   │   └── ui
│   │       └── WilsyButton.jsx
│   ├── config
│   │   └── environment.js
│   ├── constants
│   │   └── telemetryConstants.js
│   ├── context
│   │   └── SovereignAlertContext.jsx
│   ├── contexts
│   │   ├── CommandUsageContext.jsx
│   │   ├── StreamingContext.jsx
│   │   ├── authContext.jsx
│   │   ├── sovereignData.jsx
│   │   ├── sovereignMesh.jsx
│   │   ├── superadmin
│   │   │   └── AuthContext.jsx
│   │   ├── tenantContext.js
│   │   └── tenantContext.jsx
│   ├── data
│   │   ├── sourceEvidenceRequirementsMatrix.js
│   │   ├── wilsyArtifactCatalog.js
│   │   ├── wilsyCrmModuleCatalog.js
│   │   ├── wilsyKnowledgeBaseManifest.js
│   │   ├── wilsyLeadIndustryOptions.js
│   │   ├── wilsyLeadStatusOptions.js
│   │   └── wilsyLeadTitleOptions.js
│   ├── hooks
│   │   ├── createSliceHook.js
│   │   ├── useArtifactState.js
│   │   ├── useAuth.js
│   │   ├── useCompatibilityState.js
│   │   ├── useComplianceMetrics.js
│   │   ├── useDashboard.js
│   │   ├── useDashboardState.js
│   │   ├── useDigitalTwinState.js
│   │   ├── useDocumentationState.js
│   │   ├── useEventState.js
│   │   ├── useExecution.js
│   │   ├── useForensicsMetrics.js
│   │   ├── useGovernanceState.js
│   │   ├── usePredictionState.js
│   │   ├── useReportState.js
│   │   ├── useRepositoryState.js
│   │   ├── useRevenueMetrics.js
│   │   ├── useRevenueTrajectory.js
│   │   ├── useRuntimeState.js
│   │   ├── useSovereignAccess.js
│   │   ├── useSovereignData.js
│   │   ├── useSovereignMetrics.js
│   │   ├── useStreaming.js
│   │   ├── useTelemetryFeed.js
│   │   ├── useTelemetryMetrics.js
│   │   ├── useTelemetryStats.js
│   │   ├── useTenantDNA.js
│   │   ├── useTenantManagement.js
│   │   ├── useTenantRegistry.js
│   │   ├── useTenants.js
│   │   ├── useTrajectoryWithEmails.js
│   │   └── useVersionState.js
│   ├── index.css
│   ├── installHook.js
│   ├── main.jsx
│   ├── output.css
│   ├── pages
│   │   ├── Discovery.jsx
│   │   ├── superadmin
│   │   │   ├── Audit.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Reports.jsx
│   │   │   ├── Security.jsx
│   │   │   ├── System.jsx
│   │   │   ├── TEMPLATE.jsx
│   │   │   ├── TemplatePage.jsx
│   │   │   ├── Tenants.jsx
│   │   │   └── Users.jsx
│   │   └── tenant
│   ├── providers
│   │   └── DashboardStateProvider.jsx
│   ├── services
│   │   ├── CurrencyIntelligenceService.js
│   │   ├── DunningIntelligence.js
│   │   ├── ExecutiveCommandOrchestrator.js
│   │   ├── ExecutiveOperatingEngine.js
│   │   ├── ExecutiveTransformationEngine.js
│   │   ├── ForensicAuditService.js
│   │   ├── GlobalTaxEngine.js
│   │   ├── TreasurySweepManager.js
│   │   ├── WilsyAIService.js
│   │   ├── aiEthicsService.js
│   │   ├── aiSalesService.js
│   │   ├── api
│   │   │   └── tenantApi.js
│   │   ├── api.js
│   │   ├── artifacts
│   │   │   └── artifactExportService.js
│   │   ├── cooService.js
│   │   ├── crmExecutiveDnaService.js
│   │   ├── crmService.js
│   │   ├── crmSovereignIntegrationService.js
│   │   ├── customerSuccessService.js
│   │   ├── dashboardService.js
│   │   ├── dataService.js
│   │   ├── engineeringService.js
│   │   ├── executionService.js
│   │   ├── financeService.js
│   │   ├── hrService.js
│   │   ├── itService.js
│   │   ├── legalService.js
│   │   ├── longevityService.js
│   │   ├── marketingService.js
│   │   ├── pdfService.js
│   │   ├── procurementService.js
│   │   ├── productService.js
│   │   ├── quantumService.js
│   │   ├── researchService.js
│   │   ├── revenueService.js
│   │   ├── runtimeApi.js
│   │   ├── salesService.js
│   │   ├── securityService.js
│   │   ├── sourceRegistryService.js
│   │   ├── sovereignAuth.js
│   │   ├── spaceService.js
│   │   ├── streamingService.js
│   │   ├── superadmin
│   │   │   └── auth.service.js
│   │   ├── websocket
│   │   │   └── tenantWebSocket.js
│   │   ├── wilsyAccountIdentityPostureClient.js
│   │   ├── wilsyCrmCommandClient.js
│   │   ├── wilsyCrmTerminalEvidenceCockpitModel.js
│   │   ├── wilsyCrmTerminalEvidenceDashboardMountContract.js
│   │   ├── wilsyCrmTerminalEvidenceLaunchService.js
│   │   └── wilsyForensicMerkleClient.js
│   ├── state
│   │   ├── artifactStore.js
│   │   ├── compatibilityStore.js
│   │   ├── createSliceStore.js
│   │   ├── dashboardStore.js
│   │   ├── digitalTwinStore.js
│   │   ├── documentationStore.js
│   │   ├── eventStore.js
│   │   ├── executionStore.js
│   │   ├── governanceStore.js
│   │   ├── predictionStore.js
│   │   ├── reportStore.js
│   │   ├── repositoryStore.js
│   │   ├── runtimeStore.js
│   │   └── versionStore.js
│   ├── store
│   │   └── sovereignStore.js
│   ├── styles
│   │   ├── core
│   │   │   └── base.css
│   │   ├── global.css
│   │   ├── iconStyles.css
│   │   ├── pages
│   │   │   └── login.css
│   │   ├── responsive
│   │   │   └── mobile.css
│   │   ├── superadmin
│   │   │   ├── animations
│   │   │   │   ├── forensic-scan.css
│   │   │   │   ├── quantum-pulse.css
│   │   │   │   ├── risk-wave.css
│   │   │   │   └── terminal-glow.css
│   │   │   ├── colors.css
│   │   │   ├── components
│   │   │   │   ├── audit-stream.css
│   │   │   │   ├── forensic-timeline.css
│   │   │   │   ├── quantum-button.css
│   │   │   │   ├── risk-meter.css
│   │   │   │   ├── security-badge.css
│   │   │   │   ├── tenant-switcher.css
│   │   │   │   └── threat-indicator.css
│   │   │   ├── layout
│   │   │   │   ├── command-center.css
│   │   │   │   ├── forensic-panel.css
│   │   │   │   ├── global-map.css
│   │   │   │   └── terminal.css
│   │   │   ├── pages
│   │   │   │   ├── dashboard.css
│   │   │   │   ├── forensic-audit.css
│   │   │   │   ├── global-compliance.css
│   │   │   │   ├── tenant-orchestrator.css
│   │   │   │   └── wealth-vision.css
│   │   │   ├── responsive
│   │   │   │   ├── command-desktop.css
│   │   │   │   ├── command-mobile.css
│   │   │   │   ├── command-tablet.css
│   │   │   │   └── command-ultrawide.css
│   │   │   ├── superadmin.css
│   │   │   ├── themes
│   │   │   │   ├── dark-ops.css
│   │   │   │   ├── forensic.css
│   │   │   │   ├── legacy-gold.css
│   │   │   │   ├── quantum.css
│   │   │   │   ├── wilsy-aurora.css
│   │   │   │   └── wilsy-nebula-command.css
│   │   │   ├── tokens
│   │   │   │   ├── colors.css
│   │   │   │   ├── shadows.css
│   │   │   │   ├── spacing.css
│   │   │   │   ├── typography.css
│   │   │   │   └── z-index.css
│   │   │   ├── typography.css
│   │   │   └── widgets
│   │   │       ├── compliance-score.css
│   │   │       ├── jurisdiction-heatmap.css
│   │   │       ├── live-threat-map.css
│   │   │       └── transaction-monitor.css
│   │   ├── tenants
│   │   │   ├── default.css
│   │   │   └── ensafrica.css
│   │   └── tokens
│   │       ├── animations.css
│   │       ├── colors.css
│   │       ├── shadows.css
│   │       ├── spacing.css
│   │       ├── typography.css
│   │       ├── wilsy-theme-authority.css
│   │       └── z-index.css
│   ├── test
│   └── utils
│       ├── DashboardRegistry.jsx
│       ├── auditLogger.js
│       ├── cryptoCore.js
│       ├── cryptoUtils.js
│       ├── exportHelpers.js
│       ├── index.js
│       ├── logger.js
│       ├── redactSensitive.js
│       ├── sovereignClient.js
│       ├── telemetryHelper.js
│       └── wilsyPhoneGovernance.js
├── tailwind.config.js
├── test-results
│   ├── assets
│   │   ├── index-9agQl9q3.js
│   │   └── index-fUmMsp0O.css
│   ├── bg.png
│   ├── favicon.svg
│   ├── html.meta.json.gz
│   └── index.html
├── tests
│   ├── client
│   │   ├── App.test.jsx
│   │   ├── Audit.test.jsx
│   │   ├── Audit_Vault_Security.test.jsx
│   │   ├── Dashboard.test.jsx
│   │   ├── ExecutiveTransformationEngine.test.js
│   │   ├── HeaderCSS.test.js
│   │   ├── LayoutCSS.test.js
│   │   ├── Security.test.jsx
│   │   ├── SidebarCSS.test.js
│   │   ├── SovereignDashboardController.test.js
│   │   ├── SovereignLogin.test.jsx
│   │   ├── Sovereign_Audit_Vault.test.jsx
│   │   ├── Sovereign_Components.Suite.test.jsx
│   │   ├── Sovereign_Identity_Hub.test.jsx
│   │   ├── Sovereign_Node_Registry.test.jsx
│   │   ├── System.test.jsx
│   │   ├── Tenants.test.jsx
│   │   ├── auditLogger.test.js
│   │   ├── redactSensitive.test.js
│   │   └── superadmin
│   ├── components
│   │   └── analytics
│   ├── setup
│   ├── setup.js
│   └── test-utils.jsx
├── verify-files.sh
├── vite.config.js
└── vitest.config.js

104 directories, 701 files
```

## Core Service Registry & Critical Paths
| Path | Service / Component | Status |
|---|---|---|
| `./.eslintrc.json` | .eslintrc.json | Production Ready |
| `./.vscode/settings.json` | settings.json | Production Ready |
| `./.vscode/tailwind.json` | tailwind.json | Production Ready |
| `./fix_tests.js` | fix_tests.js | Production Ready |
| `./package-lock.json` | package-lock.json | Production Ready |
| `./package.json` | package.json | Production Ready |
| `./postcss.config.js` | postcss.config.js | Production Ready |
| `./src/App.jsx` | App.jsx | Production Ready |
| `./src/api/axiosConfig.js` | axiosConfig.js | Production Ready |
| `./src/assets/iconManifest.js` | iconManifest.js | Production Ready |
| `./src/components/ComplianceHUD.jsx` | ComplianceHUD.jsx | Production Ready |
| `./src/components/ErrorBoundary.jsx` | ErrorBoundary.jsx | Production Ready |
| `./src/components/ForensicsHUD.jsx` | ForensicsHUD.jsx | Production Ready |
| `./src/components/HUDAlertBanner.jsx` | HUDAlertBanner.jsx | Production Ready |
| `./src/components/RevenueHUD.jsx` | RevenueHUD.jsx | Production Ready |
| `./src/components/Security.jsx` | Security.jsx | Production Ready |
| `./src/components/SingularityDashboard.jsx` | SingularityDashboard.jsx | Production Ready |
| `./src/components/SingularityToggle.jsx` | SingularityToggle.jsx | Production Ready |
| `./src/components/SovereignContractGenerator.jsx` | SovereignContractGenerator.jsx | Production Ready |
| `./src/components/SovereignHub.jsx` | SovereignHub.jsx | Production Ready |
| `./src/components/StatCard.jsx` | StatCard.jsx | Production Ready |
| `./src/components/account/WilsyAccountCommandCenter.jsx` | WilsyAccountCommandCenter.jsx | Production Ready |
| `./src/components/account/wilsyAccountChromeRuntimeCss.js` | wilsyAccountChromeRuntimeCss.js | Production Ready |
| `./src/components/account/wilsyAccountCommandRouteContracts.js` | wilsyAccountCommandRouteContracts.js | Production Ready |
| `./src/components/account/wilsyAccountRuntimeEnhancers.js` | wilsyAccountRuntimeEnhancers.js | Production Ready |
| `./src/components/account/wilsyAccountThemeTokens.js` | wilsyAccountThemeTokens.js | Production Ready |
| `./src/components/account/wilsyNebulaCommandSkin.js` | wilsyNebulaCommandSkin.js | Production Ready |
| `./src/components/account/wilsyOperatingSkins.js` | wilsyOperatingSkins.js | Production Ready |
| `./src/components/ai_ethics/AIEthicsDashboard.jsx` | AIEthicsDashboard.jsx | Production Ready |
| `./src/components/analytics/AnalyticsDashboard.jsx` | AnalyticsDashboard.jsx | Production Ready |
| `./src/components/analytics/InvestorKPIs.jsx` | InvestorKPIs.jsx | Production Ready |
| `./src/components/analytics/QuantumForecasts.jsx` | QuantumForecasts.jsx | Production Ready |
| `./src/components/analytics/UserActivity.jsx` | UserActivity.jsx | Production Ready |
| `./src/components/artifacts/BusinessArtifactStudio.jsx` | BusinessArtifactStudio.jsx | Production Ready |
| `./src/components/auth/CovenantPortal.jsx` | CovenantPortal.jsx | Production Ready |
| `./src/components/auth/SovereignLogin.jsx` | SovereignLogin.jsx | Production Ready |
| `./src/components/auth/SovereignMfaPortal.jsx` | SovereignMfaPortal.jsx | Production Ready |
| `./src/components/auth/Sovereign_Signature_Pad.jsx` | Sovereign_Signature_Pad.jsx | Production Ready |
| `./src/components/auth/WelcomePortal.jsx` | WelcomePortal.jsx | Production Ready |
| `./src/components/billing/BillingHUD.jsx` | BillingHUD.jsx | Production Ready |
| `./src/components/billing/InvoiceSentinel.jsx` | InvoiceSentinel.jsx | Production Ready |
| `./src/components/chrome/WilsyChromePrimitives.jsx` | WilsyChromePrimitives.jsx | Production Ready |
| `./src/components/chrome/WilsyForensicMerkleShowroom.jsx` | WilsyForensicMerkleShowroom.jsx | Production Ready |
| `./src/components/compliance/ComplianceDashboard.jsx` | ComplianceDashboard.jsx | Production Ready |
| `./src/components/control-room/ExecutiveControlRoom.jsx` | ExecutiveControlRoom.jsx | Production Ready |
| `./src/components/coo/COODashboard.jsx` | COODashboard.jsx | Production Ready |
| `./src/components/crm/CRMDashboard.jsx` | CRMDashboard.jsx | Production Ready |
| `./src/components/crm/CrmSearchOutcomeRuntime.js` | CrmSearchOutcomeRuntime.js | Production Ready |
| `./src/components/crm/SovereignCRMClient.jsx` | SovereignCRMClient.jsx | Production Ready |
| `./src/components/crm/TerminalEvidenceCockpitPanel.js` | TerminalEvidenceCockpitPanel.js | Production Ready |
| `./src/components/crm/WilsyCrmRawStreamThread.jsx` | WilsyCrmRawStreamThread.jsx | Production Ready |
| `./src/components/crm/account/WilsyAccountOperatingRoom.jsx` | WilsyAccountOperatingRoom.jsx | Production Ready |
| `./src/components/crm/contact/WilsyContactOperatingRoom.jsx` | WilsyContactOperatingRoom.jsx | Production Ready |
| `./src/components/crm/lead/WilsyLeadCommandCapsule.js` | WilsyLeadCommandCapsule.js | Production Ready |
| `./src/components/crm/lead/WilsyLeadCustomViewBuilder.jsx` | WilsyLeadCustomViewBuilder.jsx | Production Ready |
| `./src/components/crm/lead/WilsyLeadEditSurface.js` | WilsyLeadEditSurface.js | Production Ready |
| `./src/components/crm/lead/WilsyLeadOperatingRoom.jsx` | WilsyLeadOperatingRoom.jsx | Production Ready |
| `./src/components/crm/meeting/WilsyMeetingOperatingRoom.jsx` | WilsyMeetingOperatingRoom.jsx | Production Ready |
| `./src/components/crm/meeting/WilsyMeetingRecordsIntelligencePanel.jsx` | WilsyMeetingRecordsIntelligencePanel.jsx | Production Ready |
| `./src/components/crm/meeting/WilsyUniversalMeetingCommandCenter.jsx` | WilsyUniversalMeetingCommandCenter.jsx | Production Ready |
| `./src/components/crm/meeting/index.js` | index.js | Production Ready |
| `./src/components/crm/meeting/workspace/WilsyMeetingCapsuleView.jsx` | WilsyMeetingCapsuleView.jsx | Production Ready |
| `./src/components/crm/meeting/workspace/WilsyMeetingEditor.jsx` | WilsyMeetingEditor.jsx | Production Ready |
| `./src/components/crm/meeting/workspace/WilsyMeetingEvidenceWorkspace.jsx` | WilsyMeetingEvidenceWorkspace.jsx | Production Ready |
| `./src/components/crm/meeting/workspace/WilsyMeetingImportWorkspace.jsx` | WilsyMeetingImportWorkspace.jsx | Production Ready |
| `./src/components/crm/meeting/workspace/WilsyMeetingParticipantResolver.jsx` | WilsyMeetingParticipantResolver.jsx | Production Ready |
| `./src/components/crm/meeting/workspace/WilsyMeetingsOverview.jsx` | WilsyMeetingsOverview.jsx | Production Ready |
| `./src/components/crm/meeting/workspace/WilsyMeetingsWorkspace.jsx` | WilsyMeetingsWorkspace.jsx | Production Ready |
| `./src/components/crm/meeting/workspace/index.js` | index.js | Production Ready |
| `./src/components/crm/rail/CrmSovereignSideRail.jsx` | CrmSovereignSideRail.jsx | Production Ready |
| `./src/components/crm/setup/WilsyCrmSetupControlPlane.jsx` | WilsyCrmSetupControlPlane.jsx | Production Ready |
| `./src/components/crm/theme/wilsyCrmThemeEngineBridge.js` | wilsyCrmThemeEngineBridge.js | Production Ready |
| `./src/components/customer_success/CustomerSuccessDashboard.jsx` | CustomerSuccessDashboard.jsx | Production Ready |
| `./src/components/data/DataDashboard.jsx` | DataDashboard.jsx | Production Ready |
| `./src/components/engineering/EngineeringDashboard.jsx` | EngineeringDashboard.jsx | Production Ready |
| `./src/components/executive/ExecutiveDashboard.jsx` | ExecutiveDashboard.jsx | Production Ready |
| `./src/components/finance/FinanceDashboard.jsx` | FinanceDashboard.jsx | Production Ready |
| `./src/components/forms/TenantOnboarding.jsx` | TenantOnboarding.jsx | Production Ready |
| `./src/components/hr/HrDashboard.jsx` | HrDashboard.jsx | Production Ready |
| `./src/components/industry/AgricultureDashboard.jsx` | AgricultureDashboard.jsx | Production Ready |
| `./src/components/industry/ConsultingDashboard.jsx` | ConsultingDashboard.jsx | Production Ready |
| `./src/components/industry/EducationDashboard.jsx` | EducationDashboard.jsx | Production Ready |
| `./src/components/industry/EnergyDashboard.jsx` | EnergyDashboard.jsx | Production Ready |
| `./src/components/industry/EntertainmentDashboard.jsx` | EntertainmentDashboard.jsx | Production Ready |
| `./src/components/industry/FinanceDashboard.jsx` | FinanceDashboard.jsx | Production Ready |
| `./src/components/industry/HealthcareDashboard.jsx` | HealthcareDashboard.jsx | Production Ready |
| `./src/components/industry/HospitalityDashboard.jsx` | HospitalityDashboard.jsx | Production Ready |
| `./src/components/industry/LegalDashboard.jsx` | LegalDashboard.jsx | Production Ready |
| `./src/components/industry/LogisticsDashboard.jsx` | LogisticsDashboard.jsx | Production Ready |
| `./src/components/industry/NonprofitDashboard.jsx` | NonprofitDashboard.jsx | Production Ready |
| `./src/components/industry/ProductionDashboard.jsx` | ProductionDashboard.jsx | Production Ready |
| `./src/components/industry/ProjectDashboard.jsx` | ProjectDashboard.jsx | Production Ready |
| `./src/components/industry/PropertyDashboard.jsx` | PropertyDashboard.jsx | Production Ready |
| `./src/components/industry/PublicDashboard.jsx` | PublicDashboard.jsx | Production Ready |
| `./src/components/industry/RetailDashboard.jsx` | RetailDashboard.jsx | Production Ready |
| `./src/components/industry/SportsDashboard.jsx` | SportsDashboard.jsx | Production Ready |
| `./src/components/industry/TechDashboard.jsx` | TechDashboard.jsx | Production Ready |
| `./src/components/intelligence/WilsyOSExecutionCanvas.jsx` | WilsyOSExecutionCanvas.jsx | Production Ready |
| `./src/components/intelligence/WilsyOSIntelligenceDock.jsx` | WilsyOSIntelligenceDock.jsx | Production Ready |
| `./src/components/intelligence/WilsyOSIntelligenceDockRuntime.jsx` | WilsyOSIntelligenceDockRuntime.jsx | Production Ready |
| `./src/components/intelligence/WilsyOSIntelligenceGlobalRuntime.jsx` | WilsyOSIntelligenceGlobalRuntime.jsx | Production Ready |
| `./src/components/intelligence/WilsyOSIntelligenceLauncher.jsx` | WilsyOSIntelligenceLauncher.jsx | Production Ready |
| `./src/components/intelligence/wilsyAIConversationHistoryEngine.js` | wilsyAIConversationHistoryEngine.js | Production Ready |
| `./src/components/intelligence/wilsyAIDynamicSuggestionEngine.js` | wilsyAIDynamicSuggestionEngine.js | Production Ready |
| `./src/components/intelligence/wilsyOperatorIntelligenceEngine.js` | wilsyOperatorIntelligenceEngine.js | Production Ready |
| `./src/components/it/ITDashboard.jsx` | ITDashboard.jsx | Production Ready |
| `./src/components/knowledge/WilsyKnowledgeBaseVault.jsx` | WilsyKnowledgeBaseVault.jsx | Production Ready |
| `./src/components/knowledge/operating/KnowledgeOperatingBar.jsx` | KnowledgeOperatingBar.jsx | Production Ready |
| `./src/components/legal/LegalDashboard.jsx` | LegalDashboard.jsx | Production Ready |
| `./src/components/longevity_sciences/LongevityDashboard.jsx` | LongevityDashboard.jsx | Production Ready |
| `./src/components/marketing/MarketingDashboard.jsx` | MarketingDashboard.jsx | Production Ready |
| `./src/components/operating-console/ExecutiveOperatingConsole.jsx` | ExecutiveOperatingConsole.jsx | Production Ready |
| `./src/components/operating-console/index.js` | index.js | Production Ready |
| `./src/components/operations/OperationsDashboard.jsx` | OperationsDashboard.jsx | Production Ready |
| `./src/components/os/WilsyOSDashboardChrome.jsx` | WilsyOSDashboardChrome.jsx | Production Ready |
| `./src/components/os/WilsyOSDashboardTopRail.jsx` | WilsyOSDashboardTopRail.jsx | Production Ready |
| `./src/components/os/wilsyDashboardChromeConfig.js` | wilsyDashboardChromeConfig.js | Production Ready |
| `./src/components/procurement/ProcurementDashboard.jsx` | ProcurementDashboard.jsx | Production Ready |
| `./src/components/product/ProductDashboard.jsx` | ProductDashboard.jsx | Production Ready |
| `./src/components/quantum_computing/QuantumDashboard.jsx` | QuantumDashboard.jsx | Production Ready |
| `./src/components/research/ResearchDashboard.jsx` | ResearchDashboard.jsx | Production Ready |
| `./src/components/sales/AISalesIntelligenceDashboard.jsx` | AISalesIntelligenceDashboard.jsx | Production Ready |
| `./src/components/sales/SalesDashboard.jsx` | SalesDashboard.jsx | Production Ready |
| `./src/components/sales/SalesRepresentativeDashboard.jsx` | SalesRepresentativeDashboard.jsx | Production Ready |
| `./src/components/security/SecurityDashboard.jsx` | SecurityDashboard.jsx | Production Ready |
| `./src/components/sovereign/AuditEntry.jsx` | AuditEntry.jsx | Production Ready |
| `./src/components/sovereign/AuditModule.jsx` | AuditModule.jsx | Production Ready |
| `./src/components/sovereign/AuditTimeline.jsx` | AuditTimeline.jsx | Production Ready |
| `./src/components/sovereign/Audit_Vault_Security.jsx` | Audit_Vault_Security.jsx | Production Ready |
| `./src/components/sovereign/BatchVerificationView.jsx` | BatchVerificationView.jsx | Production Ready |
| `./src/components/sovereign/BoardroomHUD.jsx` | BoardroomHUD.jsx | Production Ready |
| `./src/components/sovereign/CloudUplinkDashboard.jsx` | CloudUplinkDashboard.jsx | Production Ready |
| `./src/components/sovereign/CommandPalette.jsx` | CommandPalette.jsx | Production Ready |
| `./src/components/sovereign/ComplianceDashboard.jsx` | ComplianceDashboard.jsx | Production Ready |
| `./src/components/sovereign/CoverPage.jsx` | CoverPage.jsx | Production Ready |
| `./src/components/sovereign/DataOrchestrator.jsx` | DataOrchestrator.jsx | Production Ready |
| `./src/components/sovereign/DemoIgnitionButton.jsx` | DemoIgnitionButton.jsx | Production Ready |
| `./src/components/sovereign/Document_Vault_Interface.jsx` | Document_Vault_Interface.jsx | Production Ready |
| `./src/components/sovereign/ForensicsDashboard.jsx` | ForensicsDashboard.jsx | Production Ready |
| `./src/components/sovereign/FounderDashboard.jsx` | FounderDashboard.jsx | Production Ready |
| `./src/components/sovereign/GeneralDashboard.jsx` | GeneralDashboard.jsx | Production Ready |
| `./src/components/sovereign/InvestorIntelligencePortal.jsx` | InvestorIntelligencePortal.jsx | Production Ready |
| `./src/components/sovereign/MetricCard.jsx` | MetricCard.jsx | Production Ready |
| `./src/components/sovereign/NeuralNarrativeCapsule.jsx` | NeuralNarrativeCapsule.jsx | Production Ready |
| `./src/components/sovereign/NucleusFeedMonitor.jsx` | NucleusFeedMonitor.jsx | Production Ready |
| `./src/components/sovereign/QuickPanel.jsx` | QuickPanel.jsx | Production Ready |
| `./src/components/sovereign/RevenueDashboard.jsx` | RevenueDashboard.jsx | Production Ready |
| `./src/components/sovereign/RiskSentinel.jsx` | RiskSentinel.jsx | Production Ready |
| `./src/components/sovereign/SecurityManager.jsx` | SecurityManager.jsx | Production Ready |
| `./src/components/sovereign/SovereignDashboardController.jsx` | SovereignDashboardController.jsx | Production Ready |
| `./src/components/sovereign/SovereignHub.jsx` | SovereignHub.jsx | Production Ready |
| `./src/components/sovereign/SovereignLogin.jsx` | SovereignLogin.jsx | Production Ready |
| `./src/components/sovereign/SovereignNodeDashboard.jsx` | SovereignNodeDashboard.jsx | Production Ready |
| `./src/components/sovereign/SovereignOrchestrator.jsx` | SovereignOrchestrator.jsx | Production Ready |
| `./src/components/sovereign/SovereignSidebar.jsx` | SovereignSidebar.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Audit_Vault.jsx` | Sovereign_Audit_Vault.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Client_Covenant.jsx` | Sovereign_Client_Covenant.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Cloud_Gateway.jsx` | Sovereign_Cloud_Gateway.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Covenant_Modal.jsx` | Sovereign_Covenant_Modal.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Crisis_Command.jsx` | Sovereign_Crisis_Command.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Document_Vault.jsx` | Sovereign_Document_Vault.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Forensic_Exporter.jsx` | Sovereign_Forensic_Exporter.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Global_Topography.jsx` | Sovereign_Global_Topography.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Identity_Auth.jsx` | Sovereign_Identity_Auth.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Identity_Hub.jsx` | Sovereign_Identity_Hub.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Legal_Analytics.jsx` | Sovereign_Legal_Analytics.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Node_Registry.jsx` | Sovereign_Node_Registry.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Onboarding_Wizard.jsx` | Sovereign_Onboarding_Wizard.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_Revenue_Ledger.jsx` | Sovereign_Revenue_Ledger.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_StatementEngine.jsx` | Sovereign_StatementEngine.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_TenantManager.jsx` | Sovereign_TenantManager.jsx | Production Ready |
| `./src/components/sovereign/Sovereign_User_Management.jsx` | Sovereign_User_Management.jsx | Production Ready |
| `./src/components/sovereign/TenantDevTool.jsx` | TenantDevTool.jsx | Production Ready |
| `./src/components/sovereign/TenantDiscovery.jsx` | TenantDiscovery.jsx | Production Ready |
| `./src/components/sovereign/TenantManagementGrid.jsx` | TenantManagementGrid.jsx | Production Ready |
| `./src/components/sovereign/TenantSwitcher.jsx` | TenantSwitcher.jsx | Production Ready |
| `./src/components/sovereign/WilsyGlobalCommandSearch.jsx` | WilsyGlobalCommandSearch.jsx | Production Ready |
| `./src/components/space_operations/SpaceOperationsDashboard.jsx` | SpaceOperationsDashboard.jsx | Production Ready |
| `./src/components/superadmin/layout/Header.jsx` | Header.jsx | Production Ready |
| `./src/components/superadmin/layout/Sidebar.jsx` | Sidebar.jsx | Production Ready |
| `./src/components/superadmin/layout/SuperAdminLayout.jsx` | SuperAdminLayout.jsx | Production Ready |
| `./src/components/technical/TechnicalDashboard.jsx` | TechnicalDashboard.jsx | Production Ready |
| `./src/components/ui/WilsyButton.jsx` | WilsyButton.jsx | Production Ready |
| `./src/config/environment.js` | environment.js | Production Ready |
| `./src/constants/telemetryConstants.js` | telemetryConstants.js | Production Ready |
| `./src/context/SovereignAlertContext.jsx` | SovereignAlertContext.jsx | Production Ready |
| `./src/contexts/CommandUsageContext.jsx` | CommandUsageContext.jsx | Production Ready |
| `./src/contexts/StreamingContext.jsx` | StreamingContext.jsx | Production Ready |
| `./src/contexts/authContext.jsx` | authContext.jsx | Production Ready |
| `./src/contexts/sovereignData.jsx` | sovereignData.jsx | Production Ready |
| `./src/contexts/sovereignMesh.jsx` | sovereignMesh.jsx | Production Ready |
| `./src/contexts/superadmin/AuthContext.jsx` | AuthContext.jsx | Production Ready |
| `./src/contexts/tenantContext.js` | tenantContext.js | Production Ready |
| `./src/contexts/tenantContext.jsx` | tenantContext.jsx | Production Ready |
| `./src/data/sourceEvidenceRequirementsMatrix.js` | sourceEvidenceRequirementsMatrix.js | Production Ready |
| `./src/data/wilsyArtifactCatalog.js` | wilsyArtifactCatalog.js | Production Ready |
| `./src/data/wilsyCrmModuleCatalog.js` | wilsyCrmModuleCatalog.js | Production Ready |
| `./src/data/wilsyKnowledgeBaseManifest.js` | wilsyKnowledgeBaseManifest.js | Production Ready |
| `./src/data/wilsyLeadIndustryOptions.js` | wilsyLeadIndustryOptions.js | Production Ready |
| `./src/data/wilsyLeadStatusOptions.js` | wilsyLeadStatusOptions.js | Production Ready |
| `./src/data/wilsyLeadTitleOptions.js` | wilsyLeadTitleOptions.js | Production Ready |
| `./src/hooks/createSliceHook.js` | createSliceHook.js | Production Ready |
| `./src/hooks/useArtifactState.js` | useArtifactState.js | Production Ready |
| `./src/hooks/useAuth.js` | useAuth.js | Production Ready |
| `./src/hooks/useCompatibilityState.js` | useCompatibilityState.js | Production Ready |
| `./src/hooks/useComplianceMetrics.js` | useComplianceMetrics.js | Production Ready |
| `./src/hooks/useDashboard.js` | useDashboard.js | Production Ready |
| `./src/hooks/useDashboardState.js` | useDashboardState.js | Production Ready |
| `./src/hooks/useDigitalTwinState.js` | useDigitalTwinState.js | Production Ready |
| `./src/hooks/useDocumentationState.js` | useDocumentationState.js | Production Ready |
| `./src/hooks/useEventState.js` | useEventState.js | Production Ready |
| `./src/hooks/useExecution.js` | useExecution.js | Production Ready |
| `./src/hooks/useForensicsMetrics.js` | useForensicsMetrics.js | Production Ready |
| `./src/hooks/useGovernanceState.js` | useGovernanceState.js | Production Ready |
| `./src/hooks/usePredictionState.js` | usePredictionState.js | Production Ready |
| `./src/hooks/useReportState.js` | useReportState.js | Production Ready |
| `./src/hooks/useRepositoryState.js` | useRepositoryState.js | Production Ready |
| `./src/hooks/useRevenueMetrics.js` | useRevenueMetrics.js | Production Ready |
| `./src/hooks/useRevenueTrajectory.js` | useRevenueTrajectory.js | Production Ready |
| `./src/hooks/useRuntimeState.js` | useRuntimeState.js | Production Ready |
| `./src/hooks/useSovereignAccess.js` | useSovereignAccess.js | Production Ready |
| `./src/hooks/useSovereignData.js` | useSovereignData.js | Production Ready |
| `./src/hooks/useSovereignMetrics.js` | useSovereignMetrics.js | Production Ready |
| `./src/hooks/useStreaming.js` | useStreaming.js | Production Ready |
| `./src/hooks/useTelemetryFeed.js` | useTelemetryFeed.js | Production Ready |
| `./src/hooks/useTelemetryMetrics.js` | useTelemetryMetrics.js | Production Ready |
| `./src/hooks/useTelemetryStats.js` | useTelemetryStats.js | Production Ready |
| `./src/hooks/useTenantDNA.js` | useTenantDNA.js | Production Ready |
| `./src/hooks/useTenantManagement.js` | useTenantManagement.js | Production Ready |
| `./src/hooks/useTenantRegistry.js` | useTenantRegistry.js | Production Ready |
| `./src/hooks/useTenants.js` | useTenants.js | Production Ready |
| `./src/hooks/useTrajectoryWithEmails.js` | useTrajectoryWithEmails.js | Production Ready |
| `./src/hooks/useVersionState.js` | useVersionState.js | Production Ready |
| `./src/installHook.js` | installHook.js | Production Ready |
| `./src/main.jsx` | main.jsx | Production Ready |
| `./src/pages/Discovery.jsx` | Discovery.jsx | Production Ready |
| `./src/pages/superadmin/Audit.jsx` | Audit.jsx | Production Ready |
| `./src/pages/superadmin/Dashboard.jsx` | Dashboard.jsx | Production Ready |
| `./src/pages/superadmin/Reports.jsx` | Reports.jsx | Production Ready |
| `./src/pages/superadmin/Security.jsx` | Security.jsx | Production Ready |
| `./src/pages/superadmin/System.jsx` | System.jsx | Production Ready |
| `./src/pages/superadmin/TEMPLATE.jsx` | TEMPLATE.jsx | Production Ready |
| `./src/pages/superadmin/TemplatePage.jsx` | TemplatePage.jsx | Production Ready |
| `./src/pages/superadmin/Tenants.jsx` | Tenants.jsx | Production Ready |
| `./src/pages/superadmin/Users.jsx` | Users.jsx | Production Ready |
| `./src/providers/DashboardStateProvider.jsx` | DashboardStateProvider.jsx | Production Ready |
| `./src/services/CurrencyIntelligenceService.js` | CurrencyIntelligenceService.js | Production Ready |
| `./src/services/DunningIntelligence.js` | DunningIntelligence.js | Production Ready |
| `./src/services/ExecutiveCommandOrchestrator.js` | ExecutiveCommandOrchestrator.js | Production Ready |
| `./src/services/ExecutiveOperatingEngine.js` | ExecutiveOperatingEngine.js | Production Ready |
| `./src/services/ExecutiveTransformationEngine.js` | ExecutiveTransformationEngine.js | Production Ready |
| `./src/services/ForensicAuditService.js` | ForensicAuditService.js | Production Ready |
| `./src/services/GlobalTaxEngine.js` | GlobalTaxEngine.js | Production Ready |
| `./src/services/TreasurySweepManager.js` | TreasurySweepManager.js | Production Ready |
| `./src/services/WilsyAIService.js` | WilsyAIService.js | Production Ready |
| `./src/services/aiEthicsService.js` | aiEthicsService.js | Production Ready |
| `./src/services/aiSalesService.js` | aiSalesService.js | Production Ready |
| `./src/services/api.js` | api.js | Production Ready |
| `./src/services/api/tenantApi.js` | tenantApi.js | Production Ready |
| `./src/services/artifacts/artifactExportService.js` | artifactExportService.js | Production Ready |
| `./src/services/cooService.js` | cooService.js | Production Ready |
| `./src/services/crmExecutiveDnaService.js` | crmExecutiveDnaService.js | Production Ready |
| `./src/services/crmService.js` | crmService.js | Production Ready |
| `./src/services/crmSovereignIntegrationService.js` | crmSovereignIntegrationService.js | Production Ready |
| `./src/services/customerSuccessService.js` | customerSuccessService.js | Production Ready |
| `./src/services/dashboardService.js` | dashboardService.js | Production Ready |
| `./src/services/dataService.js` | dataService.js | Production Ready |
| `./src/services/engineeringService.js` | engineeringService.js | Production Ready |
| `./src/services/executionService.js` | executionService.js | Production Ready |
| `./src/services/financeService.js` | financeService.js | Production Ready |
| `./src/services/hrService.js` | hrService.js | Production Ready |
| `./src/services/itService.js` | itService.js | Production Ready |
| `./src/services/legalService.js` | legalService.js | Production Ready |
| `./src/services/longevityService.js` | longevityService.js | Production Ready |
| `./src/services/marketingService.js` | marketingService.js | Production Ready |
| `./src/services/pdfService.js` | pdfService.js | Production Ready |
| `./src/services/procurementService.js` | procurementService.js | Production Ready |
| `./src/services/productService.js` | productService.js | Production Ready |
| `./src/services/quantumService.js` | quantumService.js | Production Ready |
| `./src/services/researchService.js` | researchService.js | Production Ready |
| `./src/services/revenueService.js` | revenueService.js | Production Ready |
| `./src/services/runtimeApi.js` | runtimeApi.js | Production Ready |
| `./src/services/salesService.js` | salesService.js | Production Ready |
| `./src/services/securityService.js` | securityService.js | Production Ready |
| `./src/services/sourceRegistryService.js` | sourceRegistryService.js | Production Ready |
| `./src/services/sovereignAuth.js` | sovereignAuth.js | Production Ready |
| `./src/services/spaceService.js` | spaceService.js | Production Ready |
| `./src/services/streamingService.js` | streamingService.js | Production Ready |
| `./src/services/superadmin/auth.service.js` | auth.service.js | Production Ready |
| `./src/services/websocket/tenantWebSocket.js` | tenantWebSocket.js | Production Ready |
| `./src/services/wilsyAccountIdentityPostureClient.js` | wilsyAccountIdentityPostureClient.js | Production Ready |
| `./src/services/wilsyCrmCommandClient.js` | wilsyCrmCommandClient.js | Production Ready |
| `./src/services/wilsyCrmTerminalEvidenceCockpitModel.js` | wilsyCrmTerminalEvidenceCockpitModel.js | Production Ready |
| `./src/services/wilsyCrmTerminalEvidenceDashboardMountContract.js` | wilsyCrmTerminalEvidenceDashboardMountContract.js | Production Ready |
| `./src/services/wilsyCrmTerminalEvidenceLaunchService.js` | wilsyCrmTerminalEvidenceLaunchService.js | Production Ready |
| `./src/services/wilsyForensicMerkleClient.js` | wilsyForensicMerkleClient.js | Production Ready |
| `./src/state/artifactStore.js` | artifactStore.js | Production Ready |
| `./src/state/compatibilityStore.js` | compatibilityStore.js | Production Ready |
| `./src/state/createSliceStore.js` | createSliceStore.js | Production Ready |
| `./src/state/dashboardStore.js` | dashboardStore.js | Production Ready |
| `./src/state/digitalTwinStore.js` | digitalTwinStore.js | Production Ready |
| `./src/state/documentationStore.js` | documentationStore.js | Production Ready |
| `./src/state/eventStore.js` | eventStore.js | Production Ready |
| `./src/state/executionStore.js` | executionStore.js | Production Ready |
| `./src/state/governanceStore.js` | governanceStore.js | Production Ready |
| `./src/state/predictionStore.js` | predictionStore.js | Production Ready |
| `./src/state/reportStore.js` | reportStore.js | Production Ready |
| `./src/state/repositoryStore.js` | repositoryStore.js | Production Ready |
| `./src/state/runtimeStore.js` | runtimeStore.js | Production Ready |
| `./src/state/versionStore.js` | versionStore.js | Production Ready |
| `./src/store/sovereignStore.js` | sovereignStore.js | Production Ready |
| `./src/utils/DashboardRegistry.jsx` | DashboardRegistry.jsx | Production Ready |
| `./src/utils/auditLogger.js` | auditLogger.js | Production Ready |
| `./src/utils/cryptoCore.js` | cryptoCore.js | Production Ready |
| `./src/utils/cryptoUtils.js` | cryptoUtils.js | Production Ready |
| `./src/utils/exportHelpers.js` | exportHelpers.js | Production Ready |
| `./src/utils/index.js` | index.js | Production Ready |
| `./src/utils/logger.js` | logger.js | Production Ready |
| `./src/utils/redactSensitive.js` | redactSensitive.js | Production Ready |
| `./src/utils/sovereignClient.js` | sovereignClient.js | Production Ready |
| `./src/utils/telemetryHelper.js` | telemetryHelper.js | Production Ready |
| `./src/utils/wilsyPhoneGovernance.js` | wilsyPhoneGovernance.js | Production Ready |
| `./tailwind.config.js` | tailwind.config.js | Production Ready |
| `./test-results/assets/index-9agQl9q3.js` | index-9agQl9q3.js | Production Ready |
| `./tests/client/App.test.jsx` | App.test.jsx | Production Ready |
| `./tests/client/Audit.test.jsx` | Audit.test.jsx | Production Ready |
| `./tests/client/Audit_Vault_Security.test.jsx` | Audit_Vault_Security.test.jsx | Production Ready |
| `./tests/client/Dashboard.test.jsx` | Dashboard.test.jsx | Production Ready |
| `./tests/client/ExecutiveTransformationEngine.test.js` | ExecutiveTransformationEngine.test.js | Production Ready |
| `./tests/client/HeaderCSS.test.js` | HeaderCSS.test.js | Production Ready |
| `./tests/client/LayoutCSS.test.js` | LayoutCSS.test.js | Production Ready |
| `./tests/client/Security.test.jsx` | Security.test.jsx | Production Ready |
| `./tests/client/SidebarCSS.test.js` | SidebarCSS.test.js | Production Ready |
| `./tests/client/SovereignDashboardController.test.js` | SovereignDashboardController.test.js | Production Ready |
| `./tests/client/SovereignLogin.test.jsx` | SovereignLogin.test.jsx | Production Ready |
| `./tests/client/Sovereign_Audit_Vault.test.jsx` | Sovereign_Audit_Vault.test.jsx | Production Ready |
| `./tests/client/Sovereign_Components.Suite.test.jsx` | Sovereign_Components.Suite.test.jsx | Production Ready |
| `./tests/client/Sovereign_Identity_Hub.test.jsx` | Sovereign_Identity_Hub.test.jsx | Production Ready |
| `./tests/client/Sovereign_Node_Registry.test.jsx` | Sovereign_Node_Registry.test.jsx | Production Ready |
| `./tests/client/System.test.jsx` | System.test.jsx | Production Ready |
| `./tests/client/Tenants.test.jsx` | Tenants.test.jsx | Production Ready |
| `./tests/client/auditLogger.test.js` | auditLogger.test.js | Production Ready |
| `./tests/client/redactSensitive.test.js` | redactSensitive.test.js | Production Ready |
| `./tests/setup.js` | setup.js | Production Ready |
| `./tests/test-utils.jsx` | test-utils.jsx | Production Ready |
| `./vite.config.js` | vite.config.js | Production Ready |
| `./vitest.config.js` | vitest.config.js | Production Ready |

---
*File map successfully compiled for system ingestion.*
