# Governed canonical additions

`timonelo.factory.canonical_apply` provides an offline, reviewed apply boundary.
It does not add a public snapshot route or authorize any production additions.
The caller must stop raw file consumers and uncooperative writers and use a
dedicated exclusive checkout. Passing `offline=True` records that operational
precondition; Python cannot prove that an arbitrary external process is stopped.

Use `prepare_candidate(root, operations, baseline_commit=<full HEAD SHA>,
bound_input_sha256=<reviewed input path/hash mapping>)` for read-only preparation.
Keep its output outside the checkout. Repeating preparation against identical
inputs produces the same manifest and exact proposed four-file hashes. The
baseline records physical hashes of tracked files, all evidence, knowledge and
source files, plus the current reader generation. Bound inputs include the
actual human decision and authorization records; they are rechecked even when
untracked. A changed HEAD, file, added evidence file, generation or bound input
refuses apply.

Each operation contains `statement_id`, `event` (the complete `EvidenceEvent`
record), `create` (the existing `StatementEditor.create` arguments), `target_slug`,
`target_imo`, and `decision`. The decision contains `binding_sha256` equal to
`operation_binding(operation)`, `decision: APPROVE`, and the actual independent
reviewer's `actor`, `occurred_on`, and `note`. Copy actual recorded decisions;
do not invent a reviewer or infer approval from an observation. The reader and
event observer cannot be the approving reviewer. These records are trusted
operator inputs, not cryptographic identity authentication.

This module is a trusted local operator library, with no HTTP endpoint or
unauthenticated server integration. Its event and statement payloads are
reviewed inputs, not an automated extraction assertion. The reviewer must
verify the actual source, locator, page and exact observation before the
decision is recorded. For registered-PDF factory batches, the upstream batch
preflight verifies the rendered source region and exact claim binding. The
generic apply library does not infer natural-language meaning from a page or
establish document authenticity. A caller must not expose it directly to
untrusted request payloads or treat an arbitrary actor string as authentication.
Principal comparison normalizes Unicode compatibility forms, case and whitespace
so spelling aliases cannot create an independent reviewer.

Preparation and apply replay events, creation, support, review and publication
through the existing APIs on a private copy. Shared vessel ownership, held
artifact bytes, authority matrix, question matching and publication closure
are rechecked. Before any private event or editor write, the complete batch
rejects repeated normalized entity/question pairs, including case aliases with
matching or contradictory values. Existing statements with overlapping validity
also block contradictory values and duplicate readings of the same artifact.
Existing raw statement JSON values and review/event prefixes are preserved,
including legacy records normalized only in memory by the
editor. There is no full-store editor overlay. New conflicts refuse the batch
and require the existing human resolution flow. Artifact registry and blob
files, all ship knowledge files, and unrelated statement authority stay intact.

`apply_candidate(root, manifest, authorization, offline=True)` requires separate
explicit authorization with the exact `manifest_sha256`, actual `actor`,
`occurred_on`, and `instruction`. The hash binds the reviewed content; possessing
or computing that hash is not itself permission. Stale or altered candidates
must be prepared and reviewed again.

The transaction exclusively creates `.canonical-apply.lock`, retains immutable
manifest, authorization and before/after bytes under
`.canonical-apply-audit/<transaction>/`, and replaces only events, conflicts,
review log and statements. The replacements are individually atomic, not a
filesystem transaction. Supported Workspace/PublicationAuthority readers refuse
during the lock and retained authorities refuse after `.canonical-generation`
changes. Reopen all retained workspaces after apply. All file data is flushed
with `fsync`; power-loss durability of directory entries depends on the host
filesystem. The offline boundary remains required, including for raw readers.

A normal installation failure restores exact pre-transaction bytes while the
gate remains closed and retains decisions and observations in the audit. A
process interruption leaves the lock closed. After stopping the interrupted
process, call `recover_interrupted_apply(root, offline=True)`. Recovery uses
an exclusively created `.canonical-apply-recovery.lock` so competing recovery
calls refuse. A stale recovery claim also blocks new apply transactions;
investigate it offline and verify that no recovery process remains before
manually removing only that recovery claim. Keep the main reader gate closed
until recovery completes. Recovery checks
all backup hashes and current file hashes before restoring anything; an
unexpected edit refuses recovery and leaves the gate closed for investigation.
Recovery also checks the tracked baseline, added evidence/knowledge/source
files, and HEAD, so an edit outside the four replaced stores keeps the gate
closed. Completed recovery and corrective withdrawal verify the manifest's
content hash, completion binding, ready marker and retained output bytes before
using the journal. These integrity checks do not authenticate the journal's
author; the local checkout and operator remain the trust boundary.
An interruption before the journal's ready marker made no canonical writes.
An installation with a durable completion marker is retained; recovery only
clears its reader gate after verification. Never manually delete a lock to
make a partially installed store available.

For a completed apply, use `rollback_candidate(root, audit_directory,
actor=..., occurred_on=..., note=..., offline=True)`. This is a new corrective
transaction: it appends an audited UNKNOWN evidence-condition transition,
blocks publication for the selected additions, and preserves their evidence
events and human approvals. It refuses changed target records. UNKNOWN here
is the existing evidence-condition axis, not a newly stored answer value.
The withdrawal captures HEAD and reader generation before its private replay;
a concurrent generation change makes the corrective transaction stale.
Commit the corrective result through normal review; do not reset history.

## Historical Bellissima review artifact

The frozen manifest at
`C:/Users/Flo/.codex/worktrees/bellissima-canonical-apply/passenger-beta-phase1/reports/bellissima-canonical-apply/manifest.json`
was inspected and its physical SHA-256 verified as
`32832f33eb058a7df18865364c746806d0fc44da0d8402cc5cfd41e13ef23208`.
It describes a review-only candidate based on
`8d697990fcc7e84beccd40bc9bf1610232520409`, eight additions to a historical
410-statement baseline, and an ephemeral private output directory. It is not
the current baseline and is not an apply authorization.

`inspect_historical_manifest(path, expected_sha256=...)` checks the original
bytes, every recorded before/after candidate hash, and private-directory
availability. On inspection, all eight retained before/after files matched
their recorded hashes; the private output directory also existed. The original
four-file candidate is therefore recoverable from those retained bytes without
rebuilding it. Its old baseline still refuses application to the current
418-statement store. Directory existence alone does not establish that a
candidate is recoverable. Use original frozen bytes only after checking their
recorded output hashes. Otherwise create
a new current-baseline replay manifest and obtain review of that manifest.
Reconstruction from current source is never reported as historical byte identity.
The existing 418 canonical statements and ART-0002 files are not changed by
this implementation or its isolated tests.
