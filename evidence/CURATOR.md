# Curator workflow

Every command below is real; none of them can be short-circuited.

## 1. Register a document

```
python -m timonelo.evidence.cli artifact-create path/to/deckplan.pdf \
  --document-class cruise_line_deck_plan \
  --acquired-on 2026-08-17 \
  --acquisition-method "download from msccruises.com" \
  --publisher "MSC Cruises" --published-on 2025-11-01 \
  --version "Rev 4" --language en
```

The digest is computed from the bytes. Import ends here — it creates nothing else.

## 2. Author statements

```
python -m timonelo.evidence.cli statement-create \
  --entity cabin:MSC-BELLISSIMA:14122 \
  --question Q-0001 --statement-type cabin.deck --value 14 \
  --artifact ART-0001 --page 12 \
  --locator "Deck 14 plan, cabin table, top right" \
  --read-by your.name --read-on 2026-08-17
```

Locators are free text. Write what a second person would need to find the same
place: page, region, table, legend symbol, grid reference.

The Statement Authority Matrix is enforced here. A deck plan cannot create a
`cabin.area_sqm` statement, and the attempt is rejected rather than recorded.

## 3. Review

```
python -m timonelo.evidence.cli submit  STM-0001 --actor your.name  --on 2026-08-17
python -m timonelo.evidence.cli approve STM-0001 --actor second.person --on 2026-08-18
python -m timonelo.evidence.cli publish STM-0001 --actor second.person --on 2026-08-18
```

The person who read the document cannot publish their own statement.

## 4. Read

```
python -m timonelo.evidence.cli answer --entity cabin:MSC-BELLISSIMA:14122 --question Q-0001
python -m timonelo.evidence.cli trace  --entity cabin:MSC-BELLISSIMA:14122 --question Q-0001
python -m timonelo.evidence.cli artifact-coverage ART-0001
python -m timonelo.evidence.cli statement-inspect STM-0001
```

## Declaring a new document class

Add it to `registry/document_classes.json` with reliability, validity scope,
acquisition status and use permission stated explicitly. A class cannot be
added without declaring what it is trusted for. Curated classes in
`authority.py` cannot be overridden from the workspace.
