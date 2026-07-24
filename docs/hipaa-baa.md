# HIPAA posture & Business Associate Agreement

JIM-mini handles **Protected Health Information (PHI)** — biometrics, conditions,
journals, medical IDs. This documents which HIPAA safeguards the software already
provides and the one step that is inherently legal/operational rather than code:
the **Business Associate Agreement (BAA)**.

> This is engineering documentation, not legal advice. Have counsel review the
> BAA and your overall compliance program before handling real PHI.

## Safeguards already implemented

| HIPAA Security Rule area | In JIM-mini today |
| --- | --- |
| Access control (§164.312(a)) | Per-user bearer tokens gate every `/{user_id}` surface; tokens stored only as SHA-256 hashes; erasure revokes the token with the data. |
| Encryption at rest (§164.312(a)(2)(iv)) | PHI sealed in PDI with AES-256-GCM, AAD-bound per tenant + key. |
| Audit controls (§164.312(b)) | PDI's append-only, hash-chained audit log records every access; `GET /audit/verify` proves integrity. |
| Transmission security (§164.312(e)) | Service-to-service calls over HTTP(S); deploy behind TLS termination. |
| Individual access & amendment (§164.524) | `GET /report/{user}` and the suite export; `GET /access-log/{user}` shows the user every access to their own records. |
| Right to erasure | `DELETE /data/{user}` erases every local table and purges the user's vault records. |
| Disclosure accounting | Provider handoff is consent-gated, logged, and revocable. |

## The step that is not code: the BAA

Under HIPAA, any vendor that stores or processes PHI on your behalf (the hosting
provider, the KMS/HSM provider, and any managed database) is a **Business
Associate** and must sign a BAA before production PHI flows. This is a signature,
not a deploy — track it here.

A **production-ready BAA template** — with the required 45 C.F.R.
§ 164.504(e) provisions and an exhibit mapping each promise to the vault
control that keeps it — is maintained in the PDI repo at
[`docs/baa-template.md`](https://github.com/davidsbianchi1984/pdi/blob/main/docs/baa-template.md).
Use it as the starting point for each signature below (counsel review
required).

### Checklist before handling production PHI

- [ ] BAA signed with the **hosting** provider.
- [ ] BAA signed with the **KMS/HSM** provider backing `PDI_KEY_PROVIDER`.
- [ ] BAA signed with any **managed database / backup** provider.
- [ ] TLS enforced on every service boundary (no plaintext transport of PHI).
- [ ] `PDI_ADMIN_TOKEN` set (production PDI is not dev-open) and key rotation
      scheduled.
- [ ] Breach-notification process and workforce training in place (§164.400+).
- [ ] Data-retention windows configured per policy (PDI retention is
      per-tenant, up to forever).

### Minimal BAA template

A starting point for counsel to adapt — **not** a substitute for legal review:

> **Business Associate Agreement**
>
> This Agreement is between **[Covered Entity]** ("Covered Entity") and
> **[Business Associate]** ("Business Associate"), effective **[date]**.
>
> 1. **Permitted uses.** Business Associate may use or disclose PHI only to
>    perform the services described in the underlying service agreement, or as
>    required by law.
> 2. **Safeguards.** Business Associate will implement administrative, physical,
>    and technical safeguards that reasonably protect the confidentiality,
>    integrity, and availability of PHI, consistent with 45 CFR Part 164
>    Subpart C.
> 3. **Subcontractors.** Business Associate will ensure any subcontractor that
>    creates, receives, maintains, or transmits PHI agrees to the same
>    restrictions and conditions.
> 4. **Reporting.** Business Associate will report to Covered Entity any use or
>    disclosure not permitted by this Agreement, and any Security Incident or
>    Breach of Unsecured PHI, within **[N]** days of discovery.
> 5. **Access, amendment, accounting.** Business Associate will make PHI
>    available to satisfy Covered Entity's obligations under §164.524, §164.526,
>    and §164.528.
> 6. **Return or destruction.** On termination, Business Associate will return or
>    destroy all PHI it holds, where feasible.
> 7. **Termination.** Covered Entity may terminate if Business Associate
>    materially breaches this Agreement and fails to cure.
>
> Signed: ___________________  Date: __________

Store the executed BAA(s) with your compliance records and reference them in the
deployment runbook.
