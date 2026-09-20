import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from demo.clean_export import inspect_export, repair_export


def export(*rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["record_id", "date", "amount"])
    writer.writerows(rows)
    return stream.getvalue().encode()


class CleanExportTests(unittest.TestCase):
    def test_demo_expected_rows_and_exact_total(self):
        source = Path(__file__).parents[1] / "demo/input.csv"
        accepted, rejected, audit = inspect_export(source.read_bytes())
        self.assertEqual([r["record_id"] for r in accepted], ["00041", "00044", "00048"])
        self.assertEqual(audit["accepted_amount_total"], "20.00")
        self.assertEqual(len(rejected), 6)
        self.assertEqual(audit["input_records"], 9)

    def test_duplicates_quarantine_both_not_first_or_last(self):
        accepted, rejected, _ = inspect_export(export(["001", "2026-01-01", "1"], [" 001 ", "2026-01-01", "2"]))
        self.assertEqual(accepted, [])
        self.assertTrue(all("duplicate_record_id" in row["reasons"] for row in rejected))

    def test_wrong_shape_duplicate_does_not_allow_ambiguous_winner(self):
        accepted, rejected, _ = inspect_export(export(["001", "2026-01-01", "1"], ["001"]))
        self.assertEqual(accepted, [])
        self.assertEqual(len(rejected), 2)

    def test_decimal_sum_and_leading_zero_id(self):
        accepted, _, audit = inspect_export(export(["0001", "2024-02-29", "0.10"], ["0002", "2026-01-01", "0.20"]))
        self.assertEqual(audit["accepted_amount_total"], "0.30")
        self.assertEqual(accepted[0]["record_id"], "0001")

    def test_nonfinite_negative_locale_and_precision_rejected(self):
        for amount in ["NaN", "Infinity", "-1", "1,23", "1e3", "1.001", "", "$1.00"]:
            with self.subTest(amount=amount):
                accepted, rejected, _ = inspect_export(export(["a", "2026-01-01", amount]))
                self.assertEqual(accepted, [])
                self.assertIn("invalid_amount", rejected[0]["reasons"])

    def test_ambiguous_and_invalid_dates_rejected(self):
        for day in ["01/02/2026", "2026-02-29", "2026-1-1", "20260101", "2026-01-01T00:00:00Z"]:
            with self.subTest(day=day):
                accepted, rejected, _ = inspect_export(export(["a", day, "1"]))
                self.assertEqual(accepted, [])
                self.assertIn("invalid_iso_date", rejected[0]["reasons"])

    def test_bom_and_quoted_fields(self):
        accepted, _, _ = inspect_export(b"\xef\xbb\xbf" + export(["id,with-comma", "2026-01-01", "1"]))
        self.assertEqual(accepted[0]["record_id"], "id,with-comma")

    def test_invalid_header_and_invalid_csv_fail(self):
        for raw in [b"", b"record_id,date,date\na,b,c\n", b'record_id,date,amount\n"unterminated']:
            with self.subTest(raw=raw), self.assertRaises((ValueError, csv.Error)):
                inspect_export(raw)

    def test_empty_and_malformed_records_are_accounted_for(self):
        accepted, rejected, audit = inspect_export(export([], ["", "2026-01-01", "1"], ["a", "2026-01-01", "1", "extra"]))
        self.assertEqual(accepted, [])
        self.assertEqual(len(rejected), 3)
        self.assertEqual(audit["input_records"], 3)

    def test_source_unchanged_and_output_not_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            source, destination = Path(root) / "in.csv", Path(root) / "out"
            raw = export(["0001", "2026-01-01", "1"])
            source.write_bytes(raw)
            repair_export(source, destination)
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(json.loads((destination / "audit.json").read_text())["accepted_amount_total"], "1.00")
            before = (destination / "clean.csv").read_bytes()
            with self.assertRaises(FileExistsError):
                repair_export(source, destination)
            self.assertEqual((destination / "clean.csv").read_bytes(), before)

    def test_invalid_input_leaves_no_output_directory(self):
        with tempfile.TemporaryDirectory() as root:
            source, destination = Path(root) / "in.csv", Path(root) / "out"
            source.write_text("wrong,header\n")
            with self.assertRaises(ValueError):
                repair_export(source, destination)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
