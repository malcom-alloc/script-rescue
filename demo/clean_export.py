"""A synthetic CSV repair demonstration. Python standard library only."""

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path


COLUMNS = ["record_id", "date", "amount"]


def inspect_export(raw: bytes) -> tuple[list[dict], list[dict], dict]:
    """Validate every row; quarantine every occurrence of duplicate IDs.

    Contract: UTF-8 (optional BOM), exact header, ISO date, nonnegative USD
    amount with at most two decimal places. IDs are strings, never numbers.
    No guessing at locale, date format, currency, or intended duplicate.
    """
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    if next(reader, None) != COLUMNS:
        raise ValueError("Expected exact header: record_id,date,amount")
    rows = list(reader)
    counts = Counter(row[0].strip() for row in rows if row and row[0].strip())
    accepted, rejected = [], []
    for index, row in enumerate(rows, start=2):
        reasons = []
        if len(row) != len(COLUMNS):
            reasons.append("wrong_column_count")
        record_id = row[0].strip() if row else ""
        if not record_id:
            reasons.append("missing_record_id")
        elif counts[record_id] > 1:
            reasons.append("duplicate_record_id")
        if len(row) == len(COLUMNS):
            day, amount = row[1].strip(), row[2].strip()
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
                    raise ValueError("non-ISO date")
                date.fromisoformat(day)
            except ValueError:
                reasons.append("invalid_iso_date")
            if not re.fullmatch(r"\d+(?:\.\d{1,2})?", amount):
                reasons.append("invalid_amount")
        if reasons:
            rejected.append({"csv_record": index, "reasons": reasons, "original_fields": row})
        else:
            value = Decimal(amount)
            # Sum integer cents, avoiding Decimal context rounding on long inputs.
            accepted.append({"record_id": record_id, "date": day, "amount": f"{value:.2f}"})
    cents = sum(int(row["amount"].replace(".", "")) for row in accepted)
    total_string = f"{cents // 100}.{cents % 100:02d}"
    audit = {
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "input_records": len(rows),
        "accepted_records": len(accepted),
        "rejected_records": len(rejected),
        "accepted_amount_total": total_string,
        "currency": "USD (declared demo input contract)",
        "duplicate_policy": "quarantine all occurrences; never choose a winner",
    }
    assert len(accepted) + len(rejected) == len(rows)
    return accepted, rejected, audit


def repair_export(source: Path, destination: Path) -> dict:
    raw = source.read_bytes()
    accepted, rejected, audit = inspect_export(raw)
    # Validation finishes before creating output. Existing output is never overwritten.
    destination.mkdir(parents=True, exist_ok=False)
    with (destination / "clean.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(accepted)
    (destination / "rejected.json").write_text(json.dumps(rejected, indent=2) + "\n", encoding="utf-8")
    (destination / "audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path, help="A new output directory")
    args = parser.parse_args()
    try:
        audit = repair_export(args.source, args.destination)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        parser.exit(1, f"No completed export: {exc}\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
