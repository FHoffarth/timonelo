# Shared source document intake

`import_pdf` verifies vessel identity on the physical PDF snapshot it registers.
An explicit subject requires a one-based `source_identity_pages` entry and its
canonical name or IMO in that page's extracted text. Unknown canonical identities
refuse attributed intake. Quarantined identities may be matched for documentary
preparation in an isolated registry; canonical ownership and publication remain
blocked by the existing quarantine. Printed IMOs outside the requested vessel
set also refuse intake. Filenames, caller labels and notes cannot establish
identity. Scanned pages without extractable identity text require another
verified source; an exception does not override the held-page check.

A page printing an unapproved candidate IMO cannot be attributed to a conflicting
persisted IMO, even when the vessel name matches. It can be held without subject
attribution pending independent identity evidence and human review. The importer
does not approve candidate IMO corrections or verify MMSI assignments; the three
unresolved canonical identities and all eight audited MMSI assignments retain
their existing admission restrictions.

Multiple subjects additionally require a retained, reviewed human decision
file through `shared_document_decision_path` and its externally pinned physical
SHA-256 through `shared_document_decision_sha256`. The JSON record has these
fields:

- `schema`: `timonelo.shared-document-intake.v1`.
- `artifact_sha256`: SHA-256 of the actual reviewed PDF bytes.
- `subject_vessels`: exact sorted, unique list of canonical `IMO#######` values.
- `source_identity_pages`: exact mapping of each subject to its held identity page.
- `decision`: `APPROVE`.
- `actor`, `occurred_on`, `note`: actual recorded human decision metadata and reason
  that this document genuinely covers the listed vessels.

Keep the actual reviewed decision file under version control in the operator's
review records, and pin its physical digest in the independently reviewed intake
instruction. Copy only an actual recorded decision; never synthesize an actor,
date or approval. Changing the document, vessel set, page bindings or decision
requires a newly reviewed record and pin. No production exception or approval
is supplied by this implementation. All test decisions are isolated fixtures.

This reuses the trusted local operator boundary documented for governed
canonical apply. Hashes bind reviewed bytes; computing a hash or supplying an
actor name does not authenticate or authorize a human. This library does not
verify signatures or operator access. Do not expose these parameters directly
to untrusted request payloads; a service integration must supply its own
authenticated authorization boundary and load the previously reviewed pin from
trusted configuration. A decision file and its hash supplied together by an
untrusted caller are insufficient authorization.

The importer records the verified decision digest in the new artifact's notes
and retains normal immutable subject attribution. The external reviewed record
must remain available for audit; notes are not an authority input. Registry
deduplication still refuses changed attribution for existing physical bytes.
Intake ends at registration; it does not create evidence events, publish facts,
approve canonical additions, or establish source authenticity or media rights.
