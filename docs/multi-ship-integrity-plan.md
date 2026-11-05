# Multi-Ship Integrity Hardening

Baseline: `6be38ab4abcfdb844220b6ee260cdaa3678a77fb`.
Specification: owner mission “TIMONELO — Multi-Ship Integrity Hardening”.

One feature branch and one review. Existing architecture and all canonical data
remain unchanged. Tests must reproduce defects before corrections.

- Shared exact entity-owner/identity/artifact validation at batch, apply,
  publication and fleet boundaries; identity quarantine is not an IMO correction.
- Governed offline apply: frozen hashes, append-only additions, global IDs,
  exclusive writer lock, reader refusal, generation invalidation, retained audit
  and byte-exact rollback. No claim of multi-file filesystem atomicity.
- Claim prose generated from structured values; held PDF column validation;
  normalized duplicate/conflict detection and reviewer separation. Only exact
  previously recorded owner decisions may be reused; human authority is not a
  caller-supplied display name.
- Source import retains attribution, uses governed vault and refuses conflicting
  registrations; document identity is separate from authenticity and media rights.
- Vessel-neutral passenger formatting, edition disclosure, missing/revoked data,
  strict transport ownership. Audit eight identities/MMSIs without overwriting them.

Validation: adversarial focused suites, full backend and frontend, build,
deterministic TypeScript baseline delta, private eight-fact snapshot and historical
418/303/113 integrity, worktree fingerprints, independent final review and CI.
No merge, deployment, public snapshot, new approval, ART-0002 or canonical mutation.
