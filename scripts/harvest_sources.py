#!/usr/bin/env python3
"""
scripts/harvest_sources.py

CLI Runner for Official Source Harvester v0.1:
Example usage:
  python scripts/harvest_sources.py --cruise-line msc --document-type deck-plan --dry-run
  python scripts/harvest_sources.py --cruise-line msc --vessel msc-meraviglia --local-fixture knowledge/ships/msc-meraviglia/artifacts/MSC_MERAVIGLIA_DECKPLAN_GER.pdf
"""

import os
import sys
import argparse
import json

from timonelo.harvester.engine import HarvestEngine, HarvestRunReport


def generate_markdown_report(report: HarvestRunReport, output_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc = f"""# Source Harvest Run Report: MSC Deck Plans

**Timestamp (UTC)**: `{report.timestamp}`  
**Cruise Line**: `{report.target_cruise_line.upper()}`  
**Target Vessel**: `{report.target_vessel or 'ALL_FLEET'}`  
**Mode**: `{'DRY RUN' if report.dry_run else 'LIVE REGISTRATION'}`  

---

## Metrics Summary

| Metric | Value |
| :--- | :--- |
| **Candidates Evaluated** | {report.candidates_evaluated} |
| **Downloads Attempted** | {report.downloads_attempted} |
| **Downloads Successful** | {report.downloads_successful} |
| **Valid PDFs Verified** | {report.valid_pdfs_found} |
| **Official Sources (Tier A/B)** | {report.official_sources_verified} |
| **Third-Party Sources (Tier C)** | {report.third_party_sources} |
| **Duplicates Detected** | {report.duplicates_detected} |
| **Unresolved Vessels** | {report.unresolved_vessels} |
| **Failed Downloads** | {report.failed_downloads} |
| **Robots Blocked** | {report.robots_blocked} |

---

## Saved Artifacts

{chr(10).join(f"- `{a}`" for a in report.saved_artifacts) if report.saved_artifacts else "_No new artifacts written to vault (dry run or duplicate)._"}

## New Registry Records

{chr(10).join(f"- `{r}`" for r in report.new_records) if report.new_records else "_No new registry records._"}

---

## Detailed Results

```json
{json.dumps(report.details, indent=2)}
```
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"[REPORT] Written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Official Source Harvester CLI v0.1")
    parser.add_argument("--cruise-line", default="msc", choices=["msc"], help="Target cruise line")
    parser.add_argument("--vessel", default="msc-meraviglia", help="Target vessel ID (e.g. msc-meraviglia)")
    parser.add_argument("--document-type", default="deck-plan", help="Target document type (deck-plan)")
    parser.add_argument("--local-fixture", default=None, help="Path to local PDF fixture for offline testing")
    parser.add_argument("--dry-run", action="store_true", help="Perform discovery and verification without writing files")
    parser.add_argument("--report-out", default="knowledge/reports/source_harvest_msc_deckplans.md", help="Path to write markdown report")

    args = parser.parse_args()

    print(f"=== TIMONELO OFFICIAL SOURCE HARVESTER v0.1 ===")
    print(f"Target Line: {args.cruise_line}")
    print(f"Target Vessel: {args.vessel}")
    print(f"Doc Type: {args.document_type}")
    print(f"Dry Run: {args.dry_run}")
    if args.local_fixture:
        print(f"Local Fixture: {args.local_fixture}")

    engine = HarvestEngine()
    report = engine.run_harvest(
        vessel_id=args.vessel,
        document_type=args.document_type,
        local_fixture=args.local_fixture,
        dry_run=args.dry_run
    )

    print("\n--- RUN SUMMARY ---")
    print(f"Candidates Evaluated: {report.candidates_evaluated}")
    print(f"Valid PDFs: {report.valid_pdfs_found}")
    print(f"Official Verified: {report.official_sources_verified}")
    print(f"Duplicates: {report.duplicates_detected}")
    print(f"Saved Artifacts: {len(report.saved_artifacts)}")
    print(f"New Registry Records: {len(report.new_records)}")

    if args.report_out:
        generate_markdown_report(report, args.report_out)


if __name__ == "__main__":
    main()
