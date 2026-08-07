# Cellpinda GABA Feed B2B Operating Model

> Phase 1 activation status: source modules and Google Sheets operating master aligned on 2026-08-07. The installation workflow now applies public-page references, inquiry hardening, source-monitor fallbacks and the platform health snapshot.

## 1. Platform goal

Convert the public index from a product-information website into an operating platform that moves a qualified buyer through one controlled workflow:

`Discover → Qualify → Technical review → Sample/Pilot → Quote/PO → Lot release → Reorder`

The platform must not promise efficacy before validation. It should reduce buyer uncertainty by presenting the correct product, evidence level, technical documents, trial path, commercial requirements and contact route for the visitor's role and stage.

## 2. Operating target

### Buyer-facing target

- Understand the difference between GABA Crude and GABA Care Mix within 3 minutes.
- Select an adoption route within 5 minutes.
- Request the correct dossier, sample, pilot or quotation without re-entering previous answers.
- Receive a unique inquiry number and a response from `feed@cellpinda.com`.

### Internal target

- One product and document source of truth in Google Sheets/Drive.
- One public deployment snapshot in GitHub Pages.
- One inquiry delivery route through Google Apps Script.
- One auditable lead pipeline from inquiry to reorder.
- One health status for content freshness, documents, inquiry delivery and automation.

## 3. Operating stages

| Stage | Buyer output | Cellpinda output | Exit criterion |
|---|---|---|---|
| 1. QUALIFY | Role, species, challenge, volume and country | Qualified lead profile | Required fields complete |
| 2. REVIEW | Product, specification and evidence pack | Technical dossier and regulatory position | Buyer confirms fit or open questions |
| 3. SAMPLE/PILOT | Sample or controlled trial plan | Sample, protocol, KPI and baseline form | Trial start approval |
| 4. COMMERCIAL | MOQ, price, lead time and terms | Quote, PO checklist and supply plan | Accepted quotation or PO |
| 5. SUPPLY | Lot, CoA, shipment and traceability | Lot release package | Delivery confirmed |
| 6. REORDER | Performance and commercial review | Reorder proposal and improvement actions | Repeat order or documented no-go |

## 4. Service-level targets

These are operating targets, not contractual guarantees.

- New inquiry acknowledgement: immediate automated receipt.
- Human first response: within 1 business day.
- Initial technical document pack: within 2 business days.
- Sample/pilot feasibility decision: within 5 business days after complete input.
- Standard quotation: within 2 business days after specification and quantity confirmation.
- Non-standard OEM/ODM quotation: target date agreed after process review.

## 5. Core KPIs

### Funnel

- Qualified inquiries / total inquiries
- Dossier requests completed
- Sample approvals
- Pilot starts
- Quotes issued
- Purchase orders
- Repeat orders

### Speed

- First-response time
- Dossier turnaround time
- Sample decision time
- Quote turnaround time
- Lead time accuracy

### Quality

- Inquiry delivery success rate
- Document completeness rate
- Lot CoA release rate
- Broken-link count
- Data freshness
- Regulatory review status by country

### Commercial

- Sample-to-pilot conversion
- Pilot-to-quote conversion
- Quote-to-PO conversion
- PO-to-reorder conversion
- Gross margin by product and customer segment

## 6. Data ownership

### Google Sheets / Drive

Operational master for:

- Products, prices, MOQ, packaging and effective dates
- Specifications, CoA, certificates and technical documents
- Buyer inquiries and lead stage
- Country regulatory review
- Pilot protocol and outcome
- Quote, PO, lot and reorder references

### GitHub

Public approved snapshot and deployment code only:

- Approved public product data
- Public technical documents
- Public research/regulatory index
- Platform health snapshot

## 7. Publication rule

Public content is generated only when:

`status IN (Approved, Published) AND public = TRUE AND effective date is valid`

Draft, Review, expired and superseded records must never be treated as active public facts.

## 8. Product-claim rule

- GABA Crude 20% is presented as a provisional or approved specification according to the current lot and document status.
- Growth, FCR, gut health, heat-stress, reproduction and meat-quality effects are shown as study results or pilot hypotheses, not universal guarantees.
- Methane reduction and carbon-credit claims remain a separate research project until product-specific validation is complete.
- Antibiotic-use reduction remains a sustainability objective unless directly measured in a controlled program.

## 9. Phase-1 implementation scope

1. Add a public Buyer Deal Room with role-specific packs and operating stages.
2. Remove the legacy FormSubmit route and old recipient from the public form.
3. Add a platform health snapshot and visible update status.
4. Repair official-source monitoring with current URLs and fallback URLs.
5. Align the Google Sheets product, content, regulation, statistics and market schemas.
6. Record all changes in Change_Log.

## 10. Definition of done for Phase 1

- No `formsubmit.co` or legacy `dubaissday@cellpinda.com` remains in the active public inquiry code.
- Inquiry route points to the deployed Apps Script and `feed@cellpinda.com`.
- Buyer Deal Room opens, filters and prefills the inquiry form.
- Platform health JSON is generated and displayed.
- FDA, APVMA and OECD monitors use current or fallback official URLs.
- Products and public documents exist in the operational master.
- Browser deployment checks pass and GitHub Pages publishes the result.