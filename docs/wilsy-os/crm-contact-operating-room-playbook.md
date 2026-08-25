<!-- /* eslint-disable */ -->
# Wilsy CRM Contact Operating Room Playbook

Version: R89C-CONTACTS-GLOBAL-CREATOR-FOOTER-LOCK  
Component: `client/src/components/crm/contact/WilsyContactOperatingRoom.jsx`  
Stylesheet: `client/src/components/crm/contact/WilsyContactOperatingRoom.module.css`  
Backend command route: `/api/crm/command/contacts`  
Address intelligence route: `/api/crm/command/address/suggest`

## Collaboration

Wilson Khanyezi, Founder and CEO, mandated Contacts to leave prototype state and become a real-world CRM workspace: one screen, no wasted scroll, backend-owned create/export actions, Zoho-grade record ergonomics, and source-truth posture.

AI Engineering, Codex, mapped the visible Contacts sections, moved crowded telemetry out of the record viewport, expanded Create Contact into a full CRM command form, reused the existing address-intelligence backend contract from Leads, normalized global phone capture, and restored bottom pagination with total record accounting.

## Competitive Benchmark

Primary operator benchmark: the Founder-supplied Zoho CRM screenshots for Contacts list view, Create Contact, lead source dropdown, address information, and record footer pagination.

Official web benchmark checked: HubSpot record views and filtering documentation, which reinforces saved record views, quick filters, advanced filters, table configuration, and record-action productivity as baseline CRM expectations. Source: https://knowledge.hubspot.com/records/view-and-filter-records

## Section Map

The Contacts module must keep these sections in a fixed productivity order:

1. Header: module identity, tenant context, command utilities, theme authority.
2. Toolbar: saved view selector, search, filter, sort, insights dropdown, create contact.
3. Compact intelligence strip: outreach readiness, consent gaps, missing channels, stale touches, source graph.
4. Tabs: Records, Relationships, Consent, Sources.
5. Record workspace: filter rail plus table, never pushed below the fold by decorative cards.
6. Record footer: total records, showing range, page number, next/previous controls, page size.
7. Modal composer: full backend create command, allowed to scroll internally because it is a dense data-entry workflow.

## One-Screen Rules

Do not place metric card decks above the records workspace. Metrics belong in the toolbar insights dropdown or compact command strip.

Do not let the record table compete with repeated proof cards. The table is the primary work surface.

Do not create fake local contact rows. The create flow must submit to `/api/crm/command/contacts`, then refresh live records.

Do not downgrade to a marketing layout. Contacts is an operator surface, not a landing page.

## Create Contact Contract

The composer must capture at minimum:

- Contact owner, salutation, first name, last name, account name.
- Lead source with full CRM-style dropdown options, including Advertisement, Cold Call, Employee Referral, Online Store, Partner, X, Facebook, Public Relations, Trade Show, Web Download, Web Research, Web Mail, Chat, LinkedIn, WhatsApp, and Marketplace.
- Email, secondary email, phone, mobile, home phone, other phone, fax.
- Title and department must be picklists with predefined operator choices, not raw blank text boxes.
- Phone, mobile, home phone, other phone, fax, and assistant phone must provide country dial-code selectors and save backend payloads in international format.
- Relationship role, assistant, assistant phone, date of birth.
- Consent status and email opt-out.
- Mailing address and other address.
- Shared address intelligence with provider suggestion route `/api/crm/command/address/suggest`.
- Address intelligence must visibly present a text input and must preserve typed spaces while the user is editing.
- Description must visibly present a text area for relationship notes, consent notes and source evidence.

## Backend Payload Requirements

Every create payload must be tenant-scoped and backend-safe:

- `tenantId`
- `owner` and `contactOwner`
- `name`, `fullName`, `firstName`, `lastName`, `surname`
- `email`, `secondaryEmail`
- `phoneCountryCode`, `phone`, `mobileCountryCode`, `mobile`, `homePhoneCountryCode`, `homePhone`
- `otherPhoneCountryCode`, `otherPhone`, `faxCountryCode`, `fax`, `assistantPhoneCountryCode`, `assistantPhone`
- `accountName`, `companyName`
- `leadSource`, `consentStatus`, `emailOptOut`
- `mailingStreet`, `mailingCity`, `mailingState`, `mailingZip`, `mailingCountry`
- `otherStreet`, `otherCity`, `otherState`, `otherZip`, `otherCountry`
- `formattedAddress`, `mailingAddress`, `otherAddress`
- `addressProviderId`, `addressSourceProvider`, `addressConfidence`, `addressVerificationStatus`, `addressEvidenceReceipt`
- `description`

## Verification Commands

Run these after changing Contacts:

```bash
npm run docs:guard -- client/src/components/crm/contact/WilsyContactOperatingRoom.jsx client/src/components/crm/contact/WilsyContactOperatingRoom.module.css
npm run secrets:guard -- client/src/components/crm/contact/WilsyContactOperatingRoom.jsx client/src/components/crm/contact/WilsyContactOperatingRoom.module.css
git diff --check -- client/src/components/crm/contact/WilsyContactOperatingRoom.jsx client/src/components/crm/contact/WilsyContactOperatingRoom.module.css
npm run build
curl -I http://127.0.0.1:3000
curl -I http://127.0.0.1:5050/api/status
```

## Regression Traps

- Header text hidden when the CRM side rail opens.
- Contacts top section taller than Leads or Meetings.
- Metric deck pushing records below the fold.
- Create Contact missing email, phone, lead source, address, consent, or description fields.
- Backend create button only mutating local UI state.
- Missing bottom total records and page number.
- Address search trimming the operator's trailing space while typing.
- Phone numbers saved as local raw strings instead of international values.
- Reintroducing duplicate payload keys.
